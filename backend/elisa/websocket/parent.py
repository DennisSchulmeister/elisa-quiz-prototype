# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import traceback

from asyncio.exceptions  import CancelledError
from fastapi             import WebSocket
from fastapi             import WebSocketDisconnect
from typing              import Any
from typing              import Mapping
from typing              import Type

from ..auth.exceptions   import AuthenticationRequired
from ..auth.exceptions   import PermissionDenied
from ..auth.user         import User
from ..database.error.db import ErrorDatabase
from .types              import WebsocketMessage

class ParentWebsocketHandler:
    """
    A very minimal websocket handler that allows multiple clients to use the chat
    agent concurrently. Conversation and quizzes are currently not shared. There
    is no multi-player mode, yet. But chat messages are streamed in real-time to
    the client, which in turn renders the quiz game accordingly.
    """
    handler_classes = []

    @classmethod
    def add_handler(cls, handler: Type[Any]):
        """
        To be called at server startup to register all message handler classes.
        The classes must have been annotated with `@websocket_handler` and use
        the `@handle_message` decorator to annotate methods for each websocket
        message type.
        """
        if not hasattr(handler, "_message_handlers"):
            raise KeyError(f"Handler class is missing @websocket_handler decorator: {handler}")

        cls.handler_classes.append(handler)

    def __init__(self, websocket: WebSocket):
        """
        Initialize client-bound handler instance.
        """
        self.websocket = websocket
        self.handler_objects = [cls(parent=self) for cls in self.__class__.handler_classes]

    async def run(self):
        """
        Main loop to receive and handle web socket messages. Simply calls the respective handlers
        based on the message code.
        """
        await self.websocket.accept()

        while True:
            try:
                handled = False
                message = WebsocketMessage.model_validate_json(await self.websocket.receive_text())
                user    = User(message.jwt)

                for handler_object in self.handler_objects:
                    if message.code in handler_object._message_handlers:
                        handled = True

                        for func in handler_object._message_handlers[message.code]:
                            # Check authentication and authorization
                            if func._websocket["require_auth"] and not user.logged_in:
                                raise AuthenticationRequired()
                            
                            if func._websocket["require_scope"] and not func._websocket["require_scope"] in user.scopes:
                                raise PermissionDenied()

                            # Call handler method
                            if not func._websocket["message_type"]:
                                await func(handler_object, user=user)
                            else:
                                handler_message = func._websocket["message_type"].model_validate(message.body)
                                await func(handler_object, handler_message, user=user)
                
                if not handled:
                    error_text = f"Unknown message code: {message.code}"
                    await ErrorDatabase.insert_error_message(error_text)
                    await self.send_error(error_text)
            except (CancelledError, KeyboardInterrupt):
                print("Shutdown server", flush=True)
                break
            except (WebSocketDisconnect, RuntimeError):
                print("Client disconnected", flush=True)
                break
            except Exception as e:
                traceback.print_exc()
                print(flush=True)

                await ErrorDatabase.insert_server_exception(e)
                await self.send_error(str(e))
            
        for handler_object in self.handler_objects:
            try:
                if hasattr(handler_object, "on_connection_closed"):
                    await handler_object.on_connection_closed()
            except Exception as e:
                traceback.print_exc()
                print(flush=True)
                await ErrorDatabase.insert_server_exception(e)

    async def send_message(self, code: str, data: Mapping[str, Any] = {}):
        """
        Send a message to the client.
        """
        await self.websocket.send_json({"code": code, **data})

    async def send_error(self, text: str):
        """
        Send error message to the client.
        """
        await self.send_message("error", {"text": text})
    
    async def notify_handlers(self, key: str, value):
        """
        Send a notification to all handlers that have a `notify()` method. This is used
        to decouple the handlers and still pass data like the updated privacy settings
        once they were received.
        """
        for handler in self.handler_objects:
            try:
                if hasattr(handler, "notify"):
                    await handler.notify(key, value)
            except Exception as e:
                traceback.print_exc()
                print(flush=True)
                await ErrorDatabase.insert_server_exception(e)