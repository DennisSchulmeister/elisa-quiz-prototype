# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import datetime

from bson     import ObjectId
from pydantic import BaseModel
from typing   import Literal

class ErrorEntry(BaseModel):
    """
    Error or crash report that helps to analyze and fix bugs that occurred
    in production.
    """
    _id:           ObjectId | None = None
    timestamp:     datetime.datetime
    error_type:    Literal["server", "client", "message"]
    error_message: str
    stack_trace:   str = ""

class BugReport(BaseModel):
    """
    Manual bug report filled-in within the client.
    """
    _id:         ObjectId | None = None
    timestamp:   datetime.datetime
    username:    str
    description: str
    contact:     str
    status:      Literal["new", "in-progress", "resolved", "works-for-me", "wont-fix"]