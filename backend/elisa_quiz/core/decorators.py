# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from typing import Callable, Type, Any

def websocket_handler(cls: Type[Any]) -> Type[Any]:
    """
    Mark a class as a websocket handler class, so that its methods can be
    annotated with `@handle_message`.
    """
    cls._message_handlers = {}

    for method in cls.__dict__.values():
        if hasattr(method, "_message_code"):
            methods = cls._message_handlers.setdefault(method._message_code, [])
            methods.append(method)

    return cls

def handle_message(message_code: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Mark an instance method inside a class as a message handler method. The name
    of the message code must be passed as an argument to the decorator. The class
    must have been annotated with `@websocket_handler` and have a constructor like
    in the following example:

    ```python
    @websocket_handler
    class Handler:
        def __init__(self, parent: ParentWebsocketHandler):
            pass
    ```
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        func._message_code = message_code # type: ignore
        return func

    return decorator