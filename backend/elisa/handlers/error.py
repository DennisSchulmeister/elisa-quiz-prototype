# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import typing

from typeguard         import check_type

from ..core.decorators import handle_message
from ..core.decorators import websocket_handler
from ..core.websocket  import ParentWebsocketHandler
from ..core.websocket  import WebsocketMessage
from ..database.error  import ErrorDatabase

class FrontendErrorMessage(WebsocketMessage):
    """
    Error or exception raised in the frontend code.
    """
    error_message: str
    stack_trace:   typing.NotRequired[str]

@websocket_handler
class ErrorHandler:
    """
    Websocket message handler for crash reports and stack traces.
    """
    def __init__(self, parent: ParentWebsocketHandler):
        """
        Initialize client-bound handler instance.
        """
        self.parent = parent
    
    @handle_message("error")
    async def handle_error(self, message: FrontendErrorMessage):
        """
        Save error received from frontend.
        """
        check_type(message, FrontendErrorMessage)
        
        await ErrorDatabase.save_frontend_exception(
            error_message = message["error_message"],
            stack_trace   = message.get("stack_trace", "")
        )