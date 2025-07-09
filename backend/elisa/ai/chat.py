# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import instructor, json, os, uuid

from ..auth.user           import User
from ..database.user.db    import UserDatabase
from .agent.all            import agents
from .agent.types          import ActivityState
from .agent.types          import ActivityUpdate
from .agent.types          import AgentUpdate
from .callback             import ChatAgentCallback
from .types                import ChatKey
from .types                import ConversationMemory
from .types                import PersistedState
from .types                import PersistenceStrategy

class ChatManager:
    """
    Chat manager that provides the top-level interface to send and receive chat
    messages, applies global guard rails, maintains the conversation memory and
    mediates between the actual AI agents.

    This class manages the runtime behavior of the AI assistant, collaborating
    with the `StateManager` which manages the memory and persistent behavior.
    """

    # Number of recent messages kept verbatim before summarizing
    SHORT_TERM_N = 10

    # ================================
    # Initialization at server startup
    # ================================

    @classmethod
    def create_client(cls):
        """
        Create the LLM client object during server startup.
        """
        cls._client = instructor.from_provider(
            model = os.environ.get("ELISA_LLM_CHAT_MODEL", "openai/gpt-4.1"),
            async_client = True,
            **json.loads(os.environ.get("ELISA_LLM_KWARGS", "{}"))
        )

    #=================
    # Internal methods
    #=================

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
        self._callback              = callback
        self._user                  = user
        self._thread_id             = thread_id
        self._record_learning_topic = False
        self._language              = "en"
        self._persistence           = persistence
        self._state                 = state
        self._agents                = {agent.code: agent(self) for agent in agents}

        for code, agent in self._agents.items():
            # Note that self._state.agents is only ever used here 
            if code in self._state.agents:
                agent._state = agent.state.model_validate(self._state.agents[code])

        self._current_agent = self._agents["default"]
        self._current_activity: ActivityState | None = None

    def get_chat_key(self):
        """
        Create `ChatKey` instance for database access.
        """
        return ChatKey(username=self._user.subject, thread_id=self._thread_id)

    #=============================================
    # Methods called by the websocket handler only
    #=============================================

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

        manager = cls(
            callback    = callback,
            user        = user,
            thread_id   = thread_id or str(uuid.uuid4()),
            persistence = persistence,
            state       = state,
        )

        manager._agents["default"].greet_user()
        return manager
    
    def set_record_learning_topic(self, allow: bool):
        """
        Update flag whether the user allows to track the learning topics.
        """
        self._record_learning_topic = allow
    
    def set_language(self, language: str):
        """
        Set new language for AI generated chat messages
        """
        self._language = language

    
#     async def process_chat_message(self, msg: UserChatMessage, user: User):
#         """
#         Process chat message sent by the user by adding it to the memory and
#         feeding it to the LLM to answer. This is the main entry point to feed
#         user input into the system.
#         """
#         # Check guardrails
#         role_description = """
#             You are a vigilant content safety reviewer.
# 
#             Role: Silent observer responsible for screening each incoming message.  
# 
#             Goal: Detect and flag any content that is potentially harsh, insulting,
#             harmful, harassing, illegal, sexual or otherwise inappropriate.
#         """
# 
#         user_message = f"""
#             Task: Review the following user message. If you decide to reject the message,
#             give a short explanation of your reasoning.
# 
#             Message: {msg.content.speak}
#         """
# 
#         guard_rail = await self._client.chat.completions.create(
#                 messages = [
#                     {"role": "system", "content": role_description},
#                     {"role": "user",   "content": user_message},
#                 ],
#                 response_model = GuardRailResult,
#             )
# 
#         if guard_rail.reject:
#             return await self.send_agent_response(
#                 response = AgentResponse(
#                     message = AgentChatMessage(
#                         id      = "",
#                         content = SystemMessageContent(type="system", text=guard_rail.reasoning),
#                     )
#                 )
#             )
# 
#         # Answer or transfer to another agent
#         await self._state.add_message(msg)
#         # TODO: Let agent handle the message → Return value = programmatic hand-over
#         await self.stream_agent_response(self.answer_user_message(msg.content.speak))
    
    #==========================================================
    # Methods called by the websocket handler and the AI agents
    #==========================================================

    async def propagate_agent_update(self, update: AgentUpdate):
        """
        Distribute and process and update to an agent's state. This mutates the agent state
        in memory and persists the change.
        """
        agent = self._agents[update.agent]

        if not agent:
            raise KeyError(f"Agent not found: {update.agent}")
        
        _apply_update(agent.state, update.path, update.value)

        if self._persistence in ["server", "both"]:
            await UserDatabase.apply_agent_update(self.get_chat_key(), update)

        if self._persistence in ["client", "both"]:
            await self._callback.send_agent_update(update)

    # async def start_activity(self, activity_id: ActivityId):
    #     """
    #     Start or resume an interactive activity.
    #     """
    #     # TODO: Start activity
        
    async def propagate_activity_update(self, update: ActivityUpdate):
        """
        Distribute and process an update to the current activity's state. This mutates the
        activity state in memory and persists the change.
        """
        activity = self._state.activities[update.id]

        if not activity:
            raise KeyError(f"Activity not found: {update.id}")
        
        _apply_update(activity, update.path, update.value)

        if self._persistence in ["server", "both"]:
            await UserDatabase.apply_activity_update(self.get_chat_key(), update)

        if self._persistence in ["client", "both"]:
            await self._callback.send_activity_update(update)

    #=====================================
    # Methods called by the AI agents only
    #=====================================

#     def answer_user_message(
#         self,
#         user_message:     str,
#         task_description: str       = "",
#         context:          dict      = {},
#         handover:         list[str] = ["*"],
#     ) -> AsyncGenerator:
#         """
#         Generate an LLM response with the default system prompt. The result is the
#         streamed inner content of a speak message. This is the default method to
#         generate textual answers, used by most agents.
# 
#         Parameters:
#             user_message: Message received from the user
#             task_description: Additional system prompt to tailor the LLM response
#             context: Additional context variables to be replaced in the prompts
#             handover: Agent codes to which the LLM may hand-over ("*" = all, decision will be an extra LLM call)
#         """
#         role_description = """
#             You are ELISA – an interactive learning tutor who supports students in their learning journey.
# 
#             Role: Experienced assistant lecturer at schools and universities across diverse subjects. 
# 
#             Goal: Teach and support each student individually to help them reach their full potential.
# 
#             Backstory: Over the years, you’ve developed a student-centered teaching style. You believe
#             every learner can succeed and enjoy the process if met with empathy, encouragement, and the
#             right guidance.  
# 
#             Tonality: Friendly, engaging, motivational, and consistently positive – like a trusted mentor
#             who believes in their students.
#         """
# 
#         short_term_memory = f"""
#             Here is a summary of the previous conversation: {self._memory._short_term.previous or "None"}
# 
#             Since then the following contributions, not yet contained in the summary, were made: {self._memory._short_term.messages or "None"}
#         """
#         additional_messages = []
# 
#         if task_description:
#             additional_messages.append({"role": "system", "content": task_description})
#         
#         if handover:
#             # TODO: Hand-over prompt
#             pass
# 
#         return self._client.chat.completions.create_partial(
#             messages       = [
#                 {"role": "system", "content": role_description},
#                 {"role": "system", "content": short_term_memory},
#                 *additional_messages,
#                 {"role": "system", "content": f"Please reply in language: {self._language}"},
#                 {"role": "user",   "content": user_message},
#             ],
#             context        = context,
#             response_model = AgentResponse, # TODO: Speak only
#             stream         = True,
#         )
# 
#     async def stream_agent_response(
#         self,
#         partials:  AsyncGenerator,
#         filter_cb: FilterAgentChatMessageContent|None = None
#     ):
#         """
#         Internal method called by the agent and various activities to stream out an
#         LLM-generated agent chat message to the client and to append the message to
#         the memory. This is the default way to send messages to the client.
# 
#         Parameters:
#             partials:  Return value of `self.client.chat.completions.create_partial()`
#             filter_cb: Callback function to modify the LLM-generated message content
#         """
#         response   = None
#         message    = None
#         message_id = str(uuid.uuid4())
# 
#         async for partial in partials:
#             if filter_cb:
#                 partial = await filter_cb(partial)
# 
#             if partial.message and partial.message.ready_to_stream():
#                 response = partial
#                 message  = AgentChatMessage(source="agent", id=message_id, content=partial.message.content)
#                 await self._callback.send_agent_chat_message(message)
#         
#         if message:
#             await self._memory.add_message(message)
#         
#         if response:
#             await self._handle_agent_handover(response)
#     
#     async def send_agent_response(self, response: AgentResponse):
#         """
#         Send out an agent chat message all at once without streaming and append it
#         to the memory. This is meant for small messages where streaming doesn't improve
#         the UX.
#         """
#         if hasattr(response, "message") and response.message:
#             msg = AgentChatMessage(source="agent", id=str(uuid.uuid4()), content=response.message.content)
#             await self._callback.send_agent_chat_message(msg)
#             await self._memory.add_message(msg)
# 
#         await self._handle_agent_handover(response)
#     
#     async def _handle_agent_handover(self, response: AgentResponse):
#         """
#         Handle request from the current agent to hand-over to another one.
#         """
#         if not hasattr(response, "handover") or not response.handover:
#             return
#         
#         # TODO: Handle hand-over


#     async def add_message(self, msg: "ChatMessage|list[ChatMessage]"):
#         """
#         Add messages to the memory, creating a title once enough user messages have been
#         seen and updating the short-term and long-term memory on storage.
#         """
#         # Update transient short-term memory
#         if isinstance(msg, ChatMessage):
#             if msg.content.type == "speak":
#                 self._memory.messages.append(msg)
#         else:
#             for _msg in msg:
#                 if _msg.content.type == "speak":
#                     self._memory.messages.append(_msg)
#         
#         summary_messages = self._memory.messages[:-self.SHORT_TERM_N]
#         self._memory.messages = self._memory.messages[-self.SHORT_TERM_N:]
# 
#         # Update summary
#         if summary_messages:
#             role_description = """
#                 You are an experienced minute-taker.
# 
#                 Role: Active meeting participant responsible for writing concise and
#                 accurate minutes.  
# 
#                 Goal: Summarize the previous conversation compactly without losing essential
#                 information or nuance.  
# 
#                 Backstory: As a professional writer with extensive experience in documenting
#                 interviews and dialogues, you know how to distill conversations into clear,
#                 structured summaries that remain faithful to the original.  
# 
#                 Tone: Neutral, precise, and focused – like a diligent observer capturing what
#                 matters most.
#             """
# 
#             user_message = """
#                 Task: Update the meeting minutes and summarize the previous conversation.
# 
#                 Expected Output: A clear summary of all previous contributions, compact yet
#                 faithful to the original.
# 
#                 Previous summary: {previous}
# 
#                 What was said since then: {messages}
#             """
#             response = await self._manager._client.chat.completions.create(
#                 messages = [
#                     {"role": "system", "content": role_description},
#                     {"role": "user",   "content": user_message},
#                 ],
#                 context        = {
#                     "previous": self._memory.previous,
#                     "messages": summary_messages,
#                 },
#                 response_model = SpeakMessageContent,                
#             )
# 
#             self._memory.previous = response.speak
# 
#         # Create short title
#         if not self._title:
#             role_description = """
#                 You are a professional title editor.
# 
#                 Role: Meeting participant tasked with titling the conversation.  
#                 
#                 Goal: Distill the core of the previous conversation into a short,
#                 descriptive, and memorable title.  
#                 
#                 Backstory: With a background in editorial work and content curation,
#                 you excel at capturing the essence of discussions in just a few words.  
#                 
#                 Tone: Clear, concise, and informative – like a headline that quickly
#                 tells readers what the conversation was about.
#             """
# 
#             user_message = """
#                 Task: Write a title for the conversation.
#                 Expected Output: A short yet informative headline.
# 
#                 What was said so far: {previous}
# 
#                 {messages}
#             """
# 
#             response = await self._manager._client.chat.completions.create(
#                 messages = [
#                     {"role": "system", "content": role_description},
#                     {"role": "user",   "content": user_message},
#                 ],
#                 context        = {
#                     "previous": self._memory.previous,
#                     "messages": summary_messages,
#                 },
#                 response_model = ChatTitle,
#             )
# 
#             if response.meaningful and response.title:
#                 self._title = response.title
# 
#         # Update persistent memory
#         update = MemoryUpdate(
#             thread_id    = self._thread_id,
#             title        = self._title,
#             new_messages = [msg] if isinstance(msg, ChatMessage) else msg,
#             short_term_n = self.SHORT_TERM_N,
#             previous     = self._memory.previous,
#         )
# 
#         if self._username:
#             await UserDatabase.apply_memory_update(self._username, update)
#         else:
#             await self._manager._callback.send_memory_update(update)

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