# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from typing   import Any, Callable, Optional, Type
from pydantic import BaseModel

def websocket_handler(cls: Type[Any]) -> Type[Any]:
    """
    Mark a class as a websocket handler class, so that its methods can be annotated
    with `@handle_message`. This populates the class's `_message_handlers` dictionary
    like this:

    ```python
    {
        "message_code1": [handler_method1, handler_method2],
        "message_code2": [handler_method3],
    }
    ```
    """
    cls._message_handlers = {}

    for method in cls.__dict__.values():
        if hasattr(method, "_websocket"):
            methods = cls._message_handlers.setdefault(method._websocket["message_code"], [])
            methods.append(method)

    return cls

def handle_message(
    message_code:  str,
    message_type:  Optional[Type[BaseModel]] = None,
    require_auth:  Optional[bool] = False,
    require_scope: Optional[str] = "",
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Mark an instance method inside a class as a message handler method. The name
    of the message code must be passed as an argument to the decorator. The class
    must have been annotated with `@websocket_handler` and have a constructor like
    in example below.

    Parameters:

        message_code:  Handled message code (obligatory)
        message_type:  Pydantic model of the message body
        require_auth:  Require authenticated user
        require_scope: Require permission scope

    Example:

    ```python
    class MessageType(BaseModel):
        pass
        
    @websocket_handler
    class Handler:
        def __init__(self, parent: ParentWebsocketHandler):
            pass
        
        # Optional: Perform cleanup logic after the connection was closed
        async def on_connection_closed(self):
            pass
        
        # Optional: Receive notification from other handler
        async def notify(self, key: str, value):
            pass
        
        @handle_message("some_message", MessageType)
        async def handle_some_message(self, message: MessageType):
            pass
    ```
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        func._websocket = { # type: ignore
            "message_code":  message_code,
            "message_type":  message_type,
            "require_auth":  require_auth,
            "require_scope": require_scope,
        }
        
        return func

    return decorator