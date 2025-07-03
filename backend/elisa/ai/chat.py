# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from ..auth.user     import User
from .activity.types import ActivityTransaction
from .callback       import ChatAgentCallback
from .types          import StartChat
from .types          import UserChatMessage

class ChatAgent:
    """
    Top-level instance of the AI chat agent. Receives chat messages from the
    user, streams chat messages back to the user and applies global guard rails
    like rejecting profanity or harassments.
    """

    def __init__(self, callback: ChatAgentCallback):
        """
        Parameters:
            callback: Websocket handler with callbacks to send messages to the client
        """
        self._callback = callback
        self._record_learning_topic = False
        self._language = "en"

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
    
    async def start_chat(self, chat: StartChat, user: User):
        """
        Start new chat conversation or resume previous conversation. To resume an
        old conversation, either an authenticated user and a thread id are required
        or a thread id and the client-persisted short-term memory.
        """
    
    async def process_chat_message(self, msg: UserChatMessage, user: User):
        """
        Process chat message sent by the user.
        """
    
    async def apply_activity_transaction(self, tx: ActivityTransaction, user: User):
        """
        Handle activity update after modification by the client.
        """