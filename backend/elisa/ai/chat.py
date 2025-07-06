# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import instructor, json, os

from typing import TYPE_CHECKING

from ..auth.user     import User
from .agent.all      import agents
from .agent.base     import AgentBase
from .agent.types    import ActivityState
from .memory         import ChatMemory
from .types          import AgentChatMessage
from .types          import AgentResponse
from .types          import GuardRailResult
from .types          import SystemMessageContent

if TYPE_CHECKING:
    from .agent.types import ActivityId
    from .agent.types import ActivityUpdate
    from .agent.types import AgentUpdate
    from .agent.types import UpdateOrigin
    from .callback    import ChatAgentCallback
    from .types       import StartChat
    from .types       import UserChatMessage

class ChatManager:
    """
    Chat manager that provides the top-level interface to send and receive chat
    messages, applies global guard rails, maintains the conversation memory and
    mediates between the actual AI agents.
    """

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

    #=============================================
    # Methods called by the websocket handler only
    #=============================================

    def __init__(self, callback: ChatAgentCallback):
        """
        Parameters:
            callback: Websocket handler with callbacks to send messages to the client
        """
        self._callback = callback
        self._record_learning_topic = False
        self._language = "en"
        self._memory = ChatMemory(manager=self)

        # Initialize AI agents
        self._agents = {}
        self._current_agent: AgentBase | None = None
        self._current_activity: ActivityState | None = None     # TODO: Move into ChatMemory ??? No.
    
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
    
    async def start_chat(self, start: StartChat, user: User):
        """
        Start new chat conversation or resume previous conversation. To resume an
        old conversation, either an authenticated user and a thread id are required
        or a thread id and the client-persisted short-term memory.
        """
        self._language      = start.language
        self._agents        = {agent.code: agent(self) for agent in agents}        
        self._current_agent = self._agents["welcome-agent"]

        if user.subject and start.persist:
            # If thread_id is empty, a new chat will be started
            self._memory = await ChatMemory.restore_from_database(
                manager = self,
                username   = user.subject,
                thread_id  = start.thread_id,
            )
        else:
            # If thread_id and short_term are empty, a new chat will be started
            self._memory = ChatMemory.restore_from_client(
                manager = self,
                thread_id  = start.thread_id,
                short_term = start.short_term,
            )
        
        # TODO: Let agent handle the initial message
        # TODO: Restore agent states and activity states
        await self.stream_agent_response(self.answer_user_message("Hi!"))
    
    async def process_chat_message(self, msg: UserChatMessage, user: User):
        """
        Process chat message sent by the user by adding it to the memory and
        feeding it to the LLM to answer. This is the main entry point to feed
        user input into the system.
        """
        # Check guardrails
        role_description = """
            You are a vigilant content safety reviewer.

            Role: Silent observer responsible for screening each incoming message.  

            Goal: Detect and flag any content that is potentially harsh, insulting,
            harmful, harassing, illegal, sexual or otherwise inappropriate.
        """

        user_message = f"""
            Task: Review the following user message. If you decide to reject the message,
            give a short explanation of your reasoning.

            Message: {msg.content.speak}
        """

        guard_rail = await self._client.chat.completions.create(
                messages = [
                    {"role": "system", "content": role_description},
                    {"role": "user",   "content": user_message},
                ],
                response_model = GuardRailResult,
            )

        if guard_rail.reject:
            return await self.send_agent_response(
                response = AgentResponse(
                    message = AgentChatMessage(
                        id      = "",
                        content = SystemMessageContent(type="system", text=guard_rail.reasoning),
                    )
                )
            )

        # Answer or transfer to another agent
        await self._memory.add_message(msg)
        # TODO: Let agent handle the message → Return value = programmatic hand-over
        await self.stream_agent_response(self.answer_user_message(msg.content.speak))
    
    #==========================================================
    # Methods called by the websocket handler and the AI agents
    #==========================================================

    async def start_activity(self, activity_id: ActivityId):
        """
        Start or resume an interactive activity.
        """
        # TODO: Start activity
        
    async def propagate_activity_update(self, update: ActivityUpdate):
        """
        Distribute and process an update to the current activity's state. Depending on where
        the update originated it is either sent to the client or to the owning AI agent. In any
        case it is saved in the database, if the chat is saved server-side.
        """
        if update.origin == "agent":
            await self._callback.send_activity_update(update)
        
        # TODO: If server saves chat: Save in database

    #=====================================
    # Methods called by the AI agents only
    #=====================================

    async def propagate_agent_update(self, update: AgentUpdate):
        """
        Distribute and process and update to an agent's state. Unlike activity updates, this
        always originates from the agent. Depending on where the chat history is saved, it
        is either sent to the client or persisted in the database.
        """
        # TODO: If client saves chat:
        await self._callback.send_agent_update(update)
        # TODO: If server saves chat: Save in database




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