# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from ..core.llm       import ChatAgent
from ..core.websocket import AbstractWebsocketHandler
from ..core.websocket import ParentWebsocketHandler
from ..core.websocket import WebsocketMessage

class ChatInputMessage(WebsocketMessage):
    """
    Chat input from the user.
    """
    text: str

class ChatHandler(AbstractWebsocketHandler):
    """
    Websocket message for chat conversations and LLM-based activities.
    """
    def __init__(self, parent: ParentWebsocketHandler):
        """
        Initialize client-bound handler instance.
        """
        self.parent     = parent
        self.chat_agent = ChatAgent()
    
    # TODO: Not possible to inherit classmethod decorators
    @handle("chat_input")
    async def handle_chat_input(self, message: ChatInputMessage):
        """
        Feed chat input from user to the LLM and stream back the response.
        """
        text     = message.get("text", "")
        language = message.get("language", "en")
        await self.chat_agent.invoke_with_new_user_message(text, language, self.parent.send_message)