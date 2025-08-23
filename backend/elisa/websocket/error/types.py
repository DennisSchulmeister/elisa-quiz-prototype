# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations
from pydantic   import BaseModel

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