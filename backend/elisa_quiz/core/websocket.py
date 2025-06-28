# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import json, traceback, typing

from asyncio.exceptions import CancelledError
from fastapi            import WebSocket
from fastapi            import WebSocketDisconnect

class WebsocketMessage(typing.TypedDict):
    """
    Base type for all messages exchanged via the websocket. The only convention is
    that is contains a string code the defines the message type. Depending on the
    code other keys will be present.
    """
    code: str

class AbstractWebsocketHandler:
    """
    Abstract parent class for websocket handlers, except the parent handler. This
    provides the mechanism for handlers to register handler methods, allowing the
    parent web socket handler to instantiate a new handler instance for each new
    client connection and call the appropriate handler methods for each message.
    """

    @classmethod
    def handle(cls, message_code: str):
        """
        TODO: Typing and more
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return wrapper

        return decorator

class ParentWebsocketHandler:
    """
    A very minimal websocket handler that allows multiple clients to use the chat
    agent concurrently. Conversation and quizzes are currently not shared. There
    is no multi-player mode, yet. But chat messages are streamed in real-time to
    the frontend, which in turn renders the quiz game accordingly.
    """
    def __init__(self, websocket: WebSocket):
        """
        Initialize client-bound handler instance.
        """
        self.websocket = websocket

    async def run(self):
        """
        Main loop to accept web socket messages. Simply calls the respective handler
        function based on the received message code.
        """
        await self.websocket.accept()

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
            except (CancelledError, KeyboardInterrupt):
                print("Shutdown server", flush=True)
                break
            except (WebSocketDisconnect, RuntimeError):
                print("Client disconnected", flush=True)
                break
            except Exception as e:
                traceback.print_exc()
                print(flush=True)
                await self.send_error(str(e))

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

    async def handle_ping(self, message: WebsocketMessage):
        """
        Handle ping message. Send back pong.
        """
        await self.send_message("pong")