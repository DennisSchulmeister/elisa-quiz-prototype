# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from ..agents.prototype import ActivityData
from ..agents.prototype import ChatMessage
from ..agents.prototype import PrototypeAgent
from ..core.decorators  import handle_message
from ..core.decorators  import websocket_handler
from ..core.websocket   import ParentWebsocketHandler
from ..core.websocket   import WebsocketMessage

class ChatInputMessage(WebsocketMessage):
    """
    Chat input from the user.
    """
    text: str

@websocket_handler
class ChatHandler:
    """
    Websocket message for chat conversations and LLM-based activities.
    """
    def __init__(self, parent: ParentWebsocketHandler):
        """
        Initialize client-bound handler instance.
        """
        self.parent     = parent
        self.chat_agent = PrototypeAgent()
    
    @handle_message("chat_input")
    async def handle_chat_input(self, message: ChatInputMessage):
        """
        Feed chat input from user to the LLM and stream back the response.
        """
        text     = message.get("text", "")
        language = message.get("language", "en")

        await self.chat_agent.invoke_with_new_user_message(
            text                = text,
            language            = language,
            send_chat_message   = self.send_chat_message,
            send_start_activity = self.send_start_activity
        )
    
    async def send_chat_message(self, message: ChatMessage):
        """
        Send a chat message to the client.
        """
        await self.parent.send_message("chat_message", message)
    
    async def send_start_activity(self, data: ActivityData):
        """
        Send message to start an interactive activity to the client.
        """
        await self.parent.send_message("start_activity", data)
