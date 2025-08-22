# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import instructor, json, os, uuid

from typing             import AsyncGenerator
from typing             import cast
from typing             import TYPE_CHECKING

from ..auth.user        import User
from ..database.user.db import UserDatabase
from .agent.registry    import AgentRegistry
from .agent.types       import ActivityId
from .agent.types       import ActivityState
from .agent.types       import ActivityUpdate
from .agent.types       import AgentCode
from .agent.types       import AgentUpdate
from .callback          import ChatAgentCallback
from .shared.prompts    import default_role_description
from .shared.prompts    import default_summary_message
from .summary.registry  import SummarizerRegistry
from .title.registry    import TitleGeneratorRegistry
from .types             import AssistantChatMessage
from .types             import ChatKey
from .types             import ChatMessage
from .types             import ChooseAgentResult
from .types             import ConversationMemory
from .types             import GuardRailResult
from .types             import MemoryUpdate
from .types             import PersistedState
from .types             import PersistenceStrategy
from .types             import SpeakMessageContent
from .types             import UserChatMessage

if TYPE_CHECKING:
    from .agent.base          import AgentBase
    from .agent.default.agent import DefaultAgent

class AIAssistant:
    """
    AI assistant that provides the top-level interface to send and receive chat
    messages, applies global guard rails, maintains the conversation memory and
    mediates between internal AI agents that process the user messages.
    """

    # TODO: Configuration options
    MAX_MESSAGE_SIZE = 25000
    """Maximum allowed characters for user chat messages"""

    MAX_ROUTING_TRIES = 5
    """Maximum attempts to route a user chat message to an agent implementation"""

    # ================================
    # Initialization at server startup
    # ================================

    @classmethod
    def create_client(cls):
        """
        Create the LLM client object during server startup.
        """
        cls.client = instructor.from_provider(
            model = os.environ.get("ELISA_LLM_CHAT_MODEL", "openai/gpt-4.1"),
            async_client = True,
            **json.loads(os.environ.get("ELISA_LLM_KWARGS", "{}"))
        )

    #============================================
    # Initialization, properties, setters/getters
    #============================================

    def __init__(
        self,
        callback:    ChatAgentCallback,
        user:        User,
        thread_id:   str,
        persistence: "PersistenceStrategy",
        state:       "PersistedState",
    ):
        """
        Constructor. Not to be called directly, but used by the `create` factory-method.

        Parameters:
            callback:    Callbacks to send websocket messages to the client
            user:        Authentication and authorization context
            thread_id:   Thread ID to restore chat from client or server
            persistence: Persistence strategy of the chat
            state:       Restored chat state, when saved on the client
        """
        self.record_learning_topic = False
        self.language              = "en"
        self.user                  = user
        self.state                 = state

        self._callback        = callback
        self._thread_id       = thread_id
        self._persistence     = persistence
        self._summarizer      = SummarizerRegistry.Summarizer(assistant=self)
        self._title_generator = TitleGeneratorRegistry.TitleGenerator(assistant=self)
        
        self._agents: "dict[AgentCode, AgentBase]" = {agent.code: agent(assistant=self) for agent in AgentRegistry.get_all_agent_classes()}

        for code, agent in self._agents.items():
            # Note that self._state.agents is only ever used here 
            if code in self.state.agents:
                agent._state = agent._state.model_validate(self.state.agents[code])

        self._current_agent = self._agents["default"]
        self._current_activity: ActivityState | None = None

    @classmethod
    async def create(
        cls,
        callback:    ChatAgentCallback,
        user:        User,
        thread_id:   str                     = "",
        persistence: "PersistenceStrategy"   = "none",
        state:       "PersistedState | None" = None
    ):
        """
        Start new chat or resume previous chat. The previous chat can either be stored
        on the client, in which case `state` must be given, or in the database.

        Parameters:
            callback:    Callbacks to send websocket messages to the client
            user:        Authentication and authorization context
            persistence: Persistence strategy of the chat
            thread_id:   Thread ID to restore a previous chat
            state:       Restored chat state, when saved on the client
        """
        if not state:
            chat = None

            if thread_id and persistence in ["server", "both"]:
                key = ChatKey(username=user.subject, thread_id=thread_id)
                chat = await UserDatabase.get_chat(key)

            if chat:
                state = PersistedState(
                    title      = chat.title,
                    memory     = chat.memory,
                    agents     = chat.agents,
                    activities = chat.activities,
                )
            else:
                state = PersistedState(
                    title      = "",
                    memory     = ConversationMemory(),
                    agents     = {},
                    activities = {},
                )

        instance = cls(
            callback    = callback,
            user        = user,
            thread_id   = thread_id or str(uuid.uuid4()),
            persistence = persistence,
            state       = state,
        )

        default_agent: "DefaultAgent" = cast("DefaultAgent", instance._agents["default"])
        await default_agent.greet_user()
        return instance
    
    @property
    def chat_key(self):
        """
        Create `ChatKey` instance for database access.
        """
        return ChatKey(username=self.user.subject, thread_id=self._thread_id)

    @property
    def persistence_client(self):
        """
        Return whether the chat state is persisted client-side.
        """
        return self._persistence in ["client", "both"]

    @property
    def persistence_server(self):
        """
        Return whether the chat state is persisted server-side.
        """
        return self._persistence in ["server", "both"]

    #===================================
    # Handle incoming user chat messages
    #===================================
    
    async def process_user_chat_message(self, msg: UserChatMessage, user: User):
        """
        Process chat message sent by the user:

        1. Enforce maximum message size
        2. Apply guardrail to reject inappropriate content
        3. Add message to the chat history and conversation memory
        4. Route message to the most appropriate agent implementation
        5. Reroute message up to N times, when requested by the agent
        """
        # Reject too large message
        # TODO: List of strategy objects to validate incoming messages (size, content, guard_rails, ...)
        if len(msg.content.speak) > self.MAX_MESSAGE_SIZE:
            return await self.stream_assistant_chat_message(
                propagate         = False,
                assistant_message = AssistantChatMessage(),
                partials          = self.client.chat.completions.create_partial(
                    messages = [
                        {
                            "role": "system", 
                            "content": default_role_description,
                        }, {
                            "role": "system",
                            "content": default_summary_message,
                        }, {
                            "role": "user", 
                            "content": """
                                Task: Please explain in a short and friendly way that my last message exceeds the
                                maximum allowed size. Include, that you are designed for interactive usage – relying
                                on verbal conversation and interactive activities to aid my learning rather then just
                                summarizing copy&pasted lecture notes or exercise sheets.

                                Call to Action: Please suggest some alternative actions based on the previous conversation.

                                Language: Please respond in <language_code>{{ language }}</language_code>.
                            """,
                        }
                    ],
                    context = {
                        "memory":   self.state.memory,
                        "language": self.language,
                    },
                    response_model = SpeakMessageContent,
                ),
            )

        # Reject inappropriate message
        # TODO: Strategy object
        guard_rail = await self.client.chat.completions.create(
            messages = [
                {
                    "role": "system",
                    "content": """
                        You are a vigilant content safety reviewer.

                        Role: Silent observer responsible for screening each incoming message.  

                        Goal: Detect and flag any content that is potentially harsh, insulting,
                        harmful, harassing, illegal, sexual or otherwise inappropriate.

                        Task: Review the user message. If you decide to reject the message, give
                        a short explanation of your reasoning.

                        Language: Please respond in <language_code>{{ language }}</language_code>.
                    """,
                }, {
                    "role": "user",
                    "content": msg.content.speak,
                }
            ],
            context = {
                "message":  msg.content.speak,
                "language": self.language,
            },
            response_model = GuardRailResult,
        )

        if guard_rail.reject:
            return await self.send_assistant_chat_message(
                propagate         = False,
                assistant_message = AssistantChatMessage(
                    content = SpeakMessageContent(speak=guard_rail.explanation),
                )
            )

        # Route message to agent
        chosen_agent_code = ""
        current_agent     = ""
        current_activity  = ""

        if self._current_activity and self._current_activity.status == "running":
            chosen_agent_code = self._current_activity.agent

        for _ in range(self.MAX_ROUTING_TRIES):
            if not chosen_agent_code:
                # TODO: Strategy object
                if self._current_agent:
                    current_agent = f"""
                    <agent>
                        <agent_code>{self._current_agent.code}<agent_code>
                        <description>{self._current_agent.__doc__}</description>
                    </agent>
                    """

                if self._current_activity:
                    _agent = self._agents[self._current_activity.agent]
                    _description = _agent.activities[self._current_activity.activity] if _agent else ""

                    current_activity = f"""
                    <activity>
                        <agent_code>{self._current_activity.agent}</agent_code>
                        <activity_code>{self._current_activity.activity}</activity_code>
                        <title>{self._current_activity.title}</title>
                        <description>{_description}</description>
                    </activity>
                    """

                choose_agent = await self.client.chat.completions.create(
                    messages = [
                        {
                            "role": "system",
                            "content": """
                                You are an expert agent router.

                                Role: Triage agent responsible for routing user messages for optimum results.

                                Goal: Decide which agent is best suited to handle the incoming message.  
                            """,
                        }, {
                            "role": "system",
                            "content": default_summary_message,
                        }, {
                            "role": "system",
                            "content": """
                                Task: Review the user's message and select the most appropriate agent from the
                                provided list, based on each agent's description and supported learning activities.
                                
                                Instructions:
                                
                                {% if current_agent %}
                                * Consider both the current message and recent conversation context to make an
                                  informed decision. If unsure, prefer the currently active agent.
                                {% else %}
                                * Consider both the current message and recent conversation context to make an
                                  informed decision.
                                {% endif %}

                                {% if current_activity %}
                                * If multiple agents are suitable and the message suggests interest in choosing
                                  a different activity, ask the user to choose between the relevant options.
                                {% else %}
                                * If multiple agents are suitable, ask the user to choose between the relevant options.
                                {% endif %}

                                * If no clear match is found, choose the fallback agent named "{{ default_agent }}".

                                Available Agents: {{ all_agents }}

                                {% if current_agent %}
                                Current Agent:
                                
                                {{ current_agent }}
                                {% endif %}

                                {% if current_activity %}
                                Current Activity:
                                
                                {{ current_activity }}
                                {% endif %}

                                Language: Please respond in <language_code>{{ language }}</language_code>.
                            """,
                        }, {
                            "role": "user",
                            "content": msg.content.speak,
                        }
                    ],
                    context = {
                        "default_agent":    AgentRegistry.default_agent_code,
                        "current_agent":    current_agent,
                        "current_activity": current_activity,
                        "all_agents":       AgentRegistry.get_all_agents_prompt(),
                        "language":         self.language,
                        "memory":           self.state.memory,
                    },
                    response_model = ChooseAgentResult,
                )

                if choose_agent.agent_code:
                    chosen_agent_code = choose_agent.agent_code
                elif choose_agent.question:
                    return await self.send_assistant_chat_message(AssistantChatMessage(
                        content = SpeakMessageContent(speak=choose_agent.question),
                    ))
                
            if not chosen_agent_code or not chosen_agent_code in self._agents:
                chosen_agent_code = AgentRegistry.default_agent_code

            if self._current_activity and not self._current_activity.agent == chosen_agent_code:
                # Pause current activity when another agent was chosen
                if self._current_activity.status == "running":
                    self._current_activity.status = "paused"
                
                self._current_activity = None

            agent = self._agents[chosen_agent_code]
            result = await agent.process_chat_message(msg, user)

            if result == True:
                break
            elif result == False:
                chosen_agent_code = ""
            else:
                chosen_agent_code = result

    #=============================
    # Propagation of state updates
    #=============================

    async def create_activity(self, activity: ActivityState):
        """
        Add a new interactive activity, possibly created by the LLM.
        """
        await self.propagate_activity_update(ActivityUpdate(
            id    = activity.id,
            path  = "",
            value = activity
        ))

    async def start_activity(self, activity_id: ActivityId):
        """
        Start or resume an interactive activity. The activity must already exist, meaning it
        must already have been created by calling `propagate_activity_update()` with an update
        object that contains the initial activity state and no path.
        """
        if self._current_activity and self._current_activity.status == "running":
            await self.propagate_activity_update(ActivityUpdate(
                id    = self._current_activity.id,
                path  = "status",
                value = "paused"
            ))
        
        try:
            self._current_activity = self.state.activities[activity_id]
        except KeyError:
            return
    
        await self.propagate_activity_update(ActivityUpdate(
            id    = self._current_activity.id,
            path  = "status",
            value = "running"
        ))

    async def propagate_activity_update(self, update: ActivityUpdate):
        """
        Distribute and process an update to the current activity's state. This mutates the
        activity state in memory and persists the change.
        
        Note:
            To insert a new activity call `create_activity()`. Internally it propagates an
            activity update with an empty path and the full activity as value.
        """
        activity = self.state.activities[update.id]

        if not activity and update.path:
            raise KeyError(f"Activity not found: {update.id}")
        
        if update.path:
            # Update field inside existing activity
            _apply_update(activity, update.path, update.value)
        else:
            # Insert new activity
            self.state.activities[update.id] = update.value

        if self.persistence_server:
            await UserDatabase.apply_activity_update(self.chat_key, update)

        if self.persistence_client:
            await self._callback.send_activity_update(update)

    async def propagate_agent_update(self, update: AgentUpdate):
        """
        Distribute and process and update to an agent's state. This mutates the agent state
        in memory and persists the change.
        """
        agent = self._agents[update.agent]

        if not agent:
            raise KeyError(f"Agent not found: {update.agent}")
        
        _apply_update(agent._state, update.path, update.value)

        if self.persistence_server:
            await UserDatabase.apply_agent_update(self.chat_key, update)

        if self.persistence_client:
            await self._callback.send_agent_update(update)
        
    async def propagate_chat_messages(self, messages: list[ChatMessage|None]):
        """
        Add chat message to the conversation memory and chat history.
        """
        # Update conversation memory
        _messages: list[ChatMessage] = [message for message in messages if message]

        for message in _messages:
            self.state.memory.messages.append(message)
        
        await self._summarizer.compress_memory()
        
        # Add missing conversation title
        if not self.state.title:
            chat_title = await self._title_generator.suggest_title()

            if chat_title.meaningful and chat_title.title:
                self.state.title = chat_title.title

        # Propagate memory update
        update = MemoryUpdate(
            new_messages = _messages,
            previous     = self.state.memory.previous,
            chat_title   = self.state.title,
        )

        if self.persistence_server:
            await UserDatabase.apply_memory_update(self.chat_key, update)

        if self.persistence_client:
            await self._callback.send_memory_update(update)

    #=================================
    # Send chat messages to the client
    #=================================

    async def stream_assistant_chat_message(
        self,
        assistant_message: AssistantChatMessage,
        partials:          AsyncGenerator,
        user_message:      UserChatMessage | None = None,
        propagate:         bool = True,
    ):
        """
        Stream an assistant chat message to the client and afterwards update the chat history
        and memory accordingly. This is meant for chat-like messages to reduce the time to
        first reaction. The `finished` flag in the message indicates to the client, when the
        message has been finished streaming.

        Parameters:
            assistant_message: Prepared assistant chat message with potentially empty content

            partials: Async generator for partial message content objects. Usually
            the return value of `self._client.chat.completions.create_partial()`.

            user_message: Triggering user message to fully update the memory and chat history

            propagate: Save messages in the conversation memory
        """
        assistant_message.finished = False

        async for partial in partials:
            assistant_message.content = partial
            await self._callback.send_assistant_chat_message(assistant_message)
        
        assistant_message.finished = True
        await self._callback.send_assistant_chat_message(assistant_message)

        if propagate:
            await self.propagate_chat_messages([user_message, assistant_message])

    async def send_assistant_chat_message(
        self,
        assistant_message: AssistantChatMessage,
        user_message:      UserChatMessage | None = None,
        propagate:         bool = True,
    ):
        """
        Send an assistant chat message to the client without streaming and update the
        chat history and memory accordingly. This is meant for small messages where
        streaming doesn't improve the UX.
        
        Parameters:
            assistant_message: Assistant message to sent to the client
            user_message: Triggering user message to fully update the memory and chat history
            propagate: Save messages in the conversation memory
        """
        assistant_message.finished = True
        await self._callback.send_assistant_chat_message(assistant_message)

        if propagate:
            await self.propagate_chat_messages([user_message, assistant_message])

def _apply_update(obj, path: str, value = None):
    """
    Internal implementation for the `update_state()` and `update_activity()` methods
    that actually performs the requested update. Raises `KeyError` when the path
    cannot be fully resolved.
    """
    parent   = None
    child    = obj
    key      = 0
    is_index = False

    for subpath in path.split("."):
        # Traverse child properties
        parent = child
        key    = subpath.split("[")[0]

        if hasattr(child, key):
            child = getattr(child, key)
        elif key in child:
            child = child[key]
        else:
            parent = None
            break
    
        # Traverse list indices
        if "[" in subpath and "]" in subpath:
            for index in subpath.split("[")[1:]:
                parent = child
                key = int(index.replace("]", ""))
                child = child[key]

    if not parent:
        raise KeyError(f"Key not found: {path}")
    
    if not value and is_index:
        del parent[key]
    else:
        parent[key] = value