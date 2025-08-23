# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__   import annotations
from typing       import TYPE_CHECKING
from ..decorators import handle_message, websocket_handler

if TYPE_CHECKING:
    from ..parent import ParentWebsocketHandler

@websocket_handler
class ConnectionHandler:
    """
    Websocket message handler for crash reports and stack traces.
    """
    
    def __init__(self, parent: ParentWebsocketHandler):
        """
        Initialize client-bound handler instance.
        """
        self.parent = parent

    @handle_message("ping")
    async def handle_ping(self, **kwargs):
        """
        Handle ping message. Send back pong.
        """
        await self.parent.send_message("pong")