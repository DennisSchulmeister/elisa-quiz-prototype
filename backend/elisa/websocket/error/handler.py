# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from ...auth.user         import User
from ...database.error.db import ErrorDatabase
from ..decorators         import handle_message
from ..decorators         import websocket_handler
from ..parent             import ParentWebsocketHandler
from .types               import BugReportMessage
from .types               import ClientErrorMessage

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
    
    @handle_message("error", ClientErrorMessage)
    async def handle_error(self, message: ClientErrorMessage, **kwargs):
        """
        Save error received from client.
        """
        await ErrorDatabase.insert_client_exception(
            error_message = message.error_message,
            stack_trace   = message.stack_trace
        )
    
    @handle_message("bug_report", BugReportMessage)
    async def handle_bug_report(self, message: BugReportMessage, user: User, **kwargs):
        """
        Save manual bug report received from client.
        """
        await ErrorDatabase.insert_bug_report(
            username    = user.subject,
            description = message.description,
            contact     = message.contact,
        )