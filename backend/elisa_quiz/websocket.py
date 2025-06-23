# Elisa: AI Learning Quiz
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import asyncio, json, typing

from fastapi import WebSocket
from fastapi import WebSocketDisconnect
from .llm    import ChatAgent

class _WebsocketMessage(typing.TypedDict):
    """
    Base type for all messages exchanged via the websocket. The only convention is
    that is contains a string code the defines the message type. Depending on the
    code other keys will be present.
    """
    code: str

class _ChatInputMessage(_WebsocketMessage):
    """
    Chat input from the user.
    """
    text: str

class ChatWebSocketHandler:
    """
    A very minimal websocket handler that allows multiple clients to use the chat
    agent concurrently. Conversation and quizzes are currently not shared. There
    is no multi-player mode, yet. But chat messages are streamed in real-time to
    the frontend, which in turn renders the quiz game accordingly.
    """
    def __init__(self, websocket: WebSocket):
        """
        Each client has its own object instance. So let's initialize a few variables.
        """
        self.websocket  = websocket
        self.chat_agent = ChatAgent()

    async def run(self):
        """
        Main loop to accept web socket messages. Simply calls the respective handler
        function based on the received message code.
        """
        await self.websocket.accept()

        try:
            while True:
                try:
                    message = json.loads(await self.websocket.receive_text())

                    if not isinstance(message, dict) or "code" not in message:
                        raise ValueError("Invalid message format")
                    
                    handler = f"handle_{message["code"]}"

                    if hasattr(self, handler):
                        func = getattr(self, handler)
                        await func(message)
                    else:
                        await self.send_error(f"Unknown message code: {message["code"]}")
                except Exception as e:
                    await self.send_error(str(e))
        except WebSocketDisconnect:
            print("Client disconnected")

    async def send_message(self, code: str, data: dict = {}):
        """
        Send a message to the client.
        """
        await self.websocket.send_json({"code": code, **data})

    async def send_error(self, text: str):
        """
        Send error message to the client.
        """
        await self.send_message("error", {"text": text})

    async def handle_ping(self, message: _WebsocketMessage):
        """
        Handle ping message. Send back pong.
        """
        await self.send_message("pong")
    
    async def handle_chat_input(self, message: _ChatInputMessage):
        """
        Feed chat input from user to the LLM and stream back the response.
        """
        text = message.get("text", "")
        await self.chat_agent.user_input(text, self.send_message)