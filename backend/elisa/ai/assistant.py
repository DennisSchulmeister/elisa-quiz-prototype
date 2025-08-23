# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations

import instructor, json, os, uuid

from typing             import AsyncGenerator, cast, TYPE_CHECKING

from ..database.user.db import UserDatabase
from .agent.registry    import AgentRegistry
from .callback          import ChatAgentCallback
from .guard.registry    import GuardRailRegistry
from .router.registry   import AgentRouterRegistry
from .summary.registry  import SummarizerRegistry
from .title.registry    import TitleGeneratorRegistry

if TYPE_CHECKING:
    from ..auth.user          import User
    from .agent.base          import AgentBase
    from .agent.default.agent import DefaultAgent
    from .agent.types         import ActivityId, ActivityState, ActivityUpdate, AgentCode, AgentUpdate
    from .types               import AssistantChatMessage, ChatKey, ChatMessage, ConversationMemory, MemoryUpdate
    from .types               import PersistedState, PersistenceStrategy, SpeakMessageContent, SystemMessageContent
    from .types               import UserChatMessage

class AIAssistant:
    """
    AI assistant that provides the top-level interface to send and receive chat
    messages, applies global guard rails, maintains the conversation memory and
    mediates between internal AI agents that process the user messages.
    """

    max_routing_tries = -1
    """Maximum attempts to route a user chat message to an agent implementation"""

    # ================================
    # Initialization at server startup
    # ================================

    @classmethod
    def read_config(cls):
        """
        Create the LLM client object during server startup.
        """
        llm_chat_model    = os.environ.get("ELISA_LLM_CHAT_MODEL", "openai/gpt-4.1")
        llm_kwargs_str    = os.environ.get("ELISA_LLM_KWARGS", "{}")
        max_routing_tries = os.environ.get("ELISA_AGENT_ROUTER_TRIES", "5")

        try:
            llm_kwargs_dict = json.loads(llm_kwargs_str)
        except json.decoder.JSONDecodeError:
            raise ValueError(f"ELISA_LLM_KWARGS - Malformed JSON data: {llm_kwargs_str}")

        try:
            cls.max_routing_tries = int(max_routing_tries)
        except ValueError:
            raise ValueError(f"ELISA_AGENT_ROUTER_TRIES - Must be integer: {max_routing_tries}")

        cls.client = instructor.from_provider(
            model        = llm_chat_model,
            async_client = True,
            **llm_kwargs_dict
        )

    #============================================
    # Initialization, properties, setters/getters
    #============================================

    def __init__(
        self,
        callback:    ChatAgentCallback,
        user:        User,
        thread_id:   str,
        persistence: PersistenceStrategy,
        state:       PersistedState,
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
        # Semi-public properties
        self.record_learning_topic = False
        self.language              = "en"
        self.user                  = user
        self.state                 = state

        self.agents: dict[AgentCode, AgentBase] = {agent.code: agent(assistant=self) for agent in AgentRegistry.get_all_agent_classes()}

        for code, agent in self.agents.items():
            # Note that self._state.agents is only ever used here 
            if code in self.state.agents:
                agent._state = agent._state.model_validate(self.state.agents[code])

        self.current_agent = self.agents["default"]
        self.current_activity: ActivityState | None = None

        # Internal properties
        self._chat_key        = ChatKey(username = user.subject, thread_id = thread_id)
        self._callback        = callback
        self._thread_id       = thread_id
        self._persistence     = persistence
        self._agent_router    = AgentRouterRegistry.AgentRouter(assistant=self)
        self._summarizer      = SummarizerRegistry.Summarizer(assistant=self)
        self._title_generator = TitleGeneratorRegistry.TitleGenerator(assistant=self)
        self._guard_rails     = [GuardRail(assistant=self) for GuardRail in GuardRailRegistry.GuardRails]

    @classmethod
    async def create(
        cls,
        callback:    ChatAgentCallback,
        user:        User,
        thread_id:   str                   = "",
        persistence: PersistenceStrategy   = "none",
        state:       PersistedState | None = None
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
        default_agent: DefaultAgent = cast(DefaultAgent, instance.agents["default"])
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

        1. Apply guardrails to reject inappropriate content
        2. Add message to the chat history and conversation memory
        3. Route message to the most appropriate agent implementation
        4. Reroute message up to N times, when requested by the agent
        """
        # Apply guard rails
        for guard_rail in self._guard_rails:
            check_result = await guard_rail.check_message(msg)

            if check_result.result != "accept":
                severity = "info"

                if check_result.result == "reject-warning":
                    severity = "warning"
                elif check_result.result == "reject-critical":
                    severity = "critical"
                    await UserDatabase.insert_flagged_message(self._chat_key, msg, check_result)

                return await self.send_assistant_chat_message(
                    propagate         = False,
                    assistant_message = AssistantChatMessage(
                        content = SystemMessageContent(
                            severity = severity,
                            text     = check_result.text
                        ),
                    )
                )

        # Route message to agent
        next_agent_code  = ""

        if self.current_activity and self.current_activity.status == "running":
            next_agent_code = self.current_activity.agent

        for _ in range(self.max_routing_tries):
            # Choose next agent
            if not next_agent_code:
                next_agent = await self._agent_router.choose_agent(msg)

                if next_agent.agent_code:
                    next_agent_code = next_agent.agent_code
                elif next_agent.question:
                    return await self.send_assistant_chat_message(AssistantChatMessage(
                        content = SpeakMessageContent(speak=next_agent.question),
                    ))
                
            if not next_agent_code or not next_agent_code in self.agents:
                next_agent_code = AgentRegistry.default_agent_code

            # Pause current activity when another agent was chosen
            if self.current_activity and not self.current_activity.agent == next_agent_code:
                if self.current_activity.status == "running":
                    self.current_activity.status = "paused"
                
                self.current_activity = None

            # Let agent handle the message
            self.current_agent = self.agents[next_agent_code]
            result = await self.current_agent.process_chat_message(msg, user)

            if result == True:
                break
            elif result == False:
                next_agent_code = ""
            else:
                next_agent_code = result

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
        if self.current_activity and self.current_activity.status == "running":
            await self.propagate_activity_update(ActivityUpdate(
                id    = self.current_activity.id,
                path  = "status",
                value = "paused"
            ))
        
        try:
            self.current_activity = self.state.activities[activity_id]
        except KeyError:
            return
    
        await self.propagate_activity_update(ActivityUpdate(
            id    = self.current_activity.id,
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
        agent = self.agents[update.agent]

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
            keep_count   = self._summarizer.keep_count,
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