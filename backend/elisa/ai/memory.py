# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import uuid

from ..database.user.db import UserDatabase
from .callback          import ChatAgentInternal
from .types             import ChatMessage
from .types             import ChatTitle
from .types             import MemoryTransaction
from .types             import ShortTermMemory
from .types             import SpeakMessageContent

class ChatMemory:
    """
    Cognitive memory of an ongoing chat conversation. This class maintains
    a short-term memory that serves as additional context for the LLM, so
    that it "remembers" what was said before.
    
    It also updates the long-term memory with the full chat history, which
    is either persisted server-side or client-side. But unlike the short-term
    memory, the full message history is not kept in memory.
    """

    # Number of recent messages kept verbatim before summarizing them
    SHORT_TERM_N = 10

    def __init__(
        self,
        internal:  ChatAgentInternal,
        username:  str = "",
        thread_id: str = "",
        title:     str = "",
        short_term: ShortTermMemory | None = None,
    ):
        """
        Initialize empty memory for a new chat conversation.
        
        Note: An empty username means, that the chat is persisted by the client. Therefor
        it might be empty even though a user has been authenticated.
        """
        self._internal   = internal
        self._username   = username
        self._thread_id  = thread_id or str(uuid.uuid4())
        self._short_term = short_term or ShortTermMemory()
        self._title      = title
    
    @classmethod
    def restore_from_client(
        cls,
        internal:   ChatAgentInternal,
        thread_id:  str = "",
        title:      str = "",
        short_term: ShortTermMemory | None = None,
    ):
        """
        Create new instance from client-persisted short-term memory. No database access
        will be performed, since the client will persist the chat, if desired by the user.
        All parameters are sent by the client with values of the saved chat.

        `thread_id` and `short_term` can be left initial, when a new chat shall be started.
        Otherwise the saved values must be given.
        """
        obj = cls(
            internal   = internal,
            username   = "",
            thread_id  = thread_id,
            title      = title,
            short_term = short_term
        )

        return obj

    @classmethod
    async def restore_from_database(
        cls,
        internal:  ChatAgentInternal,
        username:  str,
        thread_id: str = "",
    ):
        """
        Create new instance from server-persisted memory or start new persisted chat,
        if it doesn't exist, yet.
        """
        if thread_id:
            chat = await UserDatabase.get_chat(username=username, thread_id=thread_id)

            if chat:
                return cls(
                    internal   = internal,
                    username   = chat.username,
                    thread_id  = chat.long_term.thread_id,
                    title      = chat.title,
                    short_term = chat.short_term,
                )
        
        return cls(
            internal = internal,
            username = username
        )

    async def add_message(self, msg: ChatMessage|list[ChatMessage]):
        """
        Add messages to the memory, creating a title once enough user messages have been
        seen and updating the short-term and long-term memory on storage.
        """
        # Update transient short-term memory
        if isinstance(msg, ChatMessage):
            self._short_term.messages.append(msg)
        else:
            for _msg in msg:
                self._short_term.messages.append(_msg)
        
        summary_messages = self._short_term.messages[:-self.SHORT_TERM_N]
        self._short_term.messages = self._short_term.messages[-self.SHORT_TERM_N:]

        # Update summary
        if summary_messages:
            role_description = """
                You are an experienced minute-taker.

                Role: Active meeting participant responsible for writing concise and
                accurate minutes.  

                Goal: Summarize the previous conversation compactly without losing essential
                information or nuance.  

                Backstory: As a professional writer with extensive experience in documenting
                interviews and dialogues, you know how to distill conversations into clear,
                structured summaries that remain faithful to the original.  

                Tone: Neutral, precise, and focused – like a diligent observer capturing what
                matters most.
            """

            user_message = """
                Task: Update the meeting minutes and summarize the previous conversation.

                Expected Output: A clear summary of all previous contributions, compact yet
                faithful to the original.

                Previous summary: {previous}

                What was said since then: {messages}
            """
            response = await self._internal._get_client().chat.completions.create(
                messages = [
                    {"role": "system", "content": role_description},
                    {"role": "user",   "content": user_message},
                ],
                context        = {
                    "previous": self._short_term.previous,
                    "messages": summary_messages,
                },
                response_model = SpeakMessageContent,                
            )

            self._short_term.previous = response.speak

        # Create short title
        if not self._title:
            role_description = """
                You are a professional title editor.

                Role: Meeting participant tasked with titling the conversation.  
                
                Goal: Distill the core of the previous conversation into a short,
                descriptive, and memorable title.  
                
                Backstory: With a background in editorial work and content curation,
                you excel at capturing the essence of discussions in just a few words.  
                
                Tone: Clear, concise, and informative – like a headline that quickly
                tells readers what the conversation was about.
            """

            user_message = """
                Task: Write a title for the conversation.
                Expected Output: A short yet informative headline.

                What was said so far: {previous}

                {messages}
            """

            response = await self._internal._get_client().chat.completions.create(
                messages = [
                    {"role": "system", "content": role_description},
                    {"role": "user",   "content": user_message},
                ],
                context        = {
                    "previous": self._short_term.previous,
                    "messages": summary_messages,
                },
                response_model = ChatTitle,
            )

            if response.meaningful and response.title:
                self._title = response.title

        # Update persistent memory
        tx = MemoryTransaction(
            thread_id    = self._thread_id,
            title        = self._title,
            new_messages = [msg] if isinstance(msg, ChatMessage) else msg,
            short_term_n = self.SHORT_TERM_N,
            previous     = self._short_term.previous,
        )

        if self._username:
            await UserDatabase.apply_memory_transaction(self._username, tx)
        else:
            await self._internal._get_callback().send_memory_transaction(tx)
