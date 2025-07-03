# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from ...ai.activity.types import ActivityTransaction
from ...ai.types          import StartChat
from ...ai.callback       import ChatAgentCallback
from ...ai.chat           import ChatAgent
from ...ai.types          import AgentChatMessage
from ...ai.types          import MemoryTransaction
from ...ai.types          import UserChatMessage
from ...auth.user         import User
from ..decorators         import handle_message
from ..decorators         import websocket_handler
from ..parent             import ParentWebsocketHandler
from .types               import ChangeLanguage

@websocket_handler
class ChatHandler(ChatAgentCallback):
    """
    Websocket message for chat conversations and interactive activities.
    """
    def __init__(self, parent: ParentWebsocketHandler):
        """
        Initialize client-bound handler instance.
        """
        self.parent     = parent
        self.chat_agent = ChatAgent(self)
    
    def notify(self, key: str, value):
        """
        Receive notification from analytics handler, whether the user allows to
        track the learning topics.
        """
        if key == "record_learning_topics":
            self.chat_agent.set_record_learning_topic(value)

    @handle_message("start_chat", StartChat)
    async def handle_start_chat(self, chat: StartChat, user: User, **kwargs):
        """
        Start new chat conversation or resume previous conversation. To resume an
        old conversation, the client sends its thread id. If the chat history is
        saved on the client, it also sends the short-term memory. Otherwise it is
        assumed, that the history is saved by the server.
        """
        await self.chat_agent.start_chat(chat, user)

    @handle_message("user_chat_message", UserChatMessage)
    async def handle_user_chat_message(self, msg: UserChatMessage, user: User, **kwargs):
        """
        Process chat message sent by the user.
        """
        await self.chat_agent.process_chat_message(msg, user)
    
    @handle_message("activity_transaction", ActivityTransaction)
    async def handle_activity_transaction(self, tx: ActivityTransaction, user: User, **kwargs):
        """
        Handle activity update after modification by the client.
        """
        await self.chat_agent.apply_activity_transaction(tx, user)
    
    @handle_message("change_language", ChangeLanguage)
    async def handle_change_language(self, change: ChangeLanguage, **kwargs):
        """
        Remember new language for AI generated chat messages.
        """
        self.chat_agent.set_language(change.language)

    #@override
    async def send_agent_chat_message(self, msg: AgentChatMessage, **kwargs):
        """
        Send an agent chat message to the client.
        """
        await self.parent.send_message("agent_chat_message", msg.model_dump())
    
    #@override
    async def send_memory_transaction(self, tx: MemoryTransaction, **kwargs):
        """
        Send conversation memory update to the client, when the client signaled
        that it wants to persist the conversation.
        """
        await self.parent.send_message("memory_transaction", tx.model_dump())
    
    #@override
    async def send_activity_transaction(self, tx: ActivityTransaction, **kwargs):
        """
        Send activity update to the client after modification by the agent.
        """
        await self.parent.send_message("activity_transaction", tx.model_dump())
