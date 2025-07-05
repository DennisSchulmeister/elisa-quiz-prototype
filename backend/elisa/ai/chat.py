# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import instructor, json, os, uuid

from typing          import AsyncGenerator

from ..auth.user     import User
from .activity.types import ActivityTransaction
from .callback       import ChatAgentCallback
from .callback       import FilterAgentChatMessageContent
from .memory         import ChatMemory
from .types          import AgentChatMessage
from .types          import AgentChatMessageContent
from .types          import ActivityMessageContent
from .types          import GuardRailResult
from .types          import SpeakMessageContent
from .types          import SystemMessageContent
from .types          import StartChat
from .types          import UserChatMessage

class ChatAgent:
    """
    Top-level instance of the AI chat agent. Receives chat messages from the
    user, streams chat messages back to the user and applies global guard rails
    like rejecting profanity or harassments.
    """

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

    def __init__(self, callback: ChatAgentCallback):
        """
        Parameters:
            callback: Websocket handler with callbacks to send messages to the client
        """
        self._callback = callback
        self._record_learning_topic = False
        self._language = "en"
        self._memory = ChatMemory(chat_agent=self)
    
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
        self._language = start.language

        if user.subject and start.persist:
            # If thread_id is empty, a new chat will be started
            self._memory = await ChatMemory.restore_from_database(
                chat_agent = self,
                username   = user.subject,
                thread_id  = start.thread_id,
            )
        else:
            # If thread_id and short_term are empty, a new chat will be started
            self._memory = ChatMemory.restore_from_client(
                chat_agent = self,
                thread_id  = start.thread_id,
                short_term = start.short_term,
            )
        
        await self._stream_agent_message(self._answer_user_message("Hi!"))
    
    async def process_chat_message(self, msg: UserChatMessage, user: User):
        """
        Process chat message sent by the user by adding it to the memory and
        feeding it to the LLM to answer.
        """
        # Check guardrails
        role_description = """
        You are a vigilant content safety reviewer.

        Role: Silent observer responsible for screening each incoming message.  

        Goal: Detect and flag any content that is potentially harsh, harmful,
        harassing, illegal, sexual or otherwise inappropriate.  

        Backstory: With experience in moderation and digital communication ethics,
        you ensure that conversations remain safe, respectful, and lawful without
        disrupting the flow.  

        Tone: Discreet, objective, and consistent – like a trusted safety net quietly
        ensuring a respectful space.
        """

        user_message = f"""
            Task: Review the following user message. If you decide to reject the message,
            give a short explanation of your reasoning.

            {msg.content.speak}
        """

        guard_rail = await self._client.chat.completions.create(
                messages = [
                    {"role": "system", "content": role_description},
                    {"role": "user",   "content": user_message},
                ],
                response_model = GuardRailResult,
            )

        if guard_rail.reject:
            return await self._send_agent_message(
                content = SystemMessageContent(type="system", text=guard_rail.reasoning),
            )

        # Answer or transfer to another agent
        await self._memory.add_message(msg)
        await self._stream_agent_message(self._answer_user_message(msg.content.speak))

        # TODO: Enable transfer to sub-agent, prefer agent of currently running activity (if any)
    
    async def restart_activity(self, content: ActivityMessageContent, user: User, **kwargs):
        """
        Restart an interactive activity from the chat history.
        """
        # TODO:

    async def apply_activity_transaction(self, tx: ActivityTransaction, user: User):
        """
        Handle activity update after modification by the client.
        """
        # TODO:
    
    def _answer_user_message(self, user_message: str, context = {}) -> AsyncGenerator:
        """
        Generate an LLM response with the default system prompt. The result is the
        streamed inner content of a speak message.
        """
        role_description = """
            You are ELISA – an interactive learning tutor who supports students in their learning journey.

            Role: Experienced assistant lecturer at schools and universities across diverse subjects. 

            Goal: Teach and support each student individually to help them reach their full potential.

            Backstory: Over the years, you’ve developed a student-centered teaching style. You believe
            every learner can succeed and enjoy the process if met with empathy, encouragement, and the
            right guidance.  

            Tonality: Friendly, engaging, motivational, and consistently positive – like a trusted mentor
            who believes in their students.
        """

        short_term_memory = f"""
        Here is a summary of the previous conversation: {self._memory._short_term.previous or "None"}

        Since then the following contributions, not yet contained in the summary, were made: {self._memory._short_term.messages or "None"}
        """

        return self._client.chat.completions.create_partial(
            messages = [
                {"role": "system", "content": role_description},
                {"role": "system", "content": short_term_memory},
                {"role": "system", "content": f"Please reply in language: {self._language}"},
                {"role": "user",   "content": user_message},
            ],
            context        = context,
            response_model = SpeakMessageContent,
            stream         = True,
        )

    async def _stream_agent_message(
        self,
        partials:  AsyncGenerator,
        filter_cb: FilterAgentChatMessageContent|None = None
    ):
        """
        Internal method called by the agent and various activities to stream out an
        LLM-generated agent chat message to the client and to append the message to
        the memory. This is the default way to send messages to the client.

        Parameters:
            partials:  Return value of `self.client.chat.completions.create_partial()`
            filter_cb: Callback function to modify the LLM-generated message content
        """
        msg    = None
        msg_id = str(uuid.uuid4())

        async for partial in partials:
            if filter_cb:
                partial = await filter_cb(partial)

            if partial.ready_to_stream():
                msg = AgentChatMessage(source="agent", id=msg_id, content=partial)
                await self._callback.send_agent_chat_message(msg)
        
        if msg:
            await self._memory.add_message(msg)
    
    async def _send_agent_message(self, content: AgentChatMessageContent):
        """
        Send out an agent chat message all at once without streaming and append it
        to the memory. This is meant for small messages where streaming doesn't improve
        the UX.
        """
        msg = AgentChatMessage(source="agent", id=str(uuid.uuid4()), content=content)
        await self._callback.send_agent_chat_message(msg)
        await self._memory.add_message(msg)