# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__        import annotations
from pydantic          import BaseModel
from typing            import TYPE_CHECKING

from ...database.error import ErrorDatabase
from ._decorators      import handle_message, websocket_handler

if TYPE_CHECKING:
    from ...auth.user import User
    from ..parent     import ParentWebsocketHandler

class ClientErrorMessage(BaseModel):
    """
    Error or exception raised in the client code.
    """
    error_message: str
    """The error message (exception message)"""

    stack_trace: str = ""
    """Optional stack trace of where the error occurred"""

class BugReportMessage(BaseModel):
    """
    Manual bug report filled-in within the client.
    """
    description: str
    """The actual bug report entered by the user"""

    contact: str = ""
    """Optional contact data to reply to the user"""

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