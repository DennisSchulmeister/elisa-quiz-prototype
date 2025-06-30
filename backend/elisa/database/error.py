# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import datetime, traceback

from bson                            import ObjectId
from typing                          import Literal
from typing                          import NotRequired
from typing                          import TypedDict
from pymongo.asynchronous.collection import AsyncCollection

from ..core.database                 import mongo_client
from ..core.database                 import now
from ..core.typing                   import check_type

class ErrorEntry(TypedDict):
    """
    Error or crash report that helps to analyze and fix bugs that occurred
    in production.
    """
    _id:           NotRequired[ObjectId]
    timestamp:     datetime.datetime
    error_type:    Literal["backend", "frontend", "message"]
    error_message: str
    stack_trace:   NotRequired[str]

class BugReport(TypedDict):
    """
    Manual bug report filled-in within the frontend.
    """
    _id:         NotRequired[ObjectId]
    timestamp:   datetime.datetime
    description: str
    contact:     str
    status:      Literal["new", "in-progress", "resolved", "works-for-me", "wont-fix"]

class ErrorDatabase:
    """
    Database for crash reports and stack traces
    """
    db = mongo_client.error
    """Mongo database instance"""

    errors: AsyncCollection[ErrorEntry] = mongo_client.error.errors
    """Error collection"""

    bug_reports: AsyncCollection[BugReport] = mongo_client.error.bug_reports
    """Manual bug reports"""

    @classmethod
    async def insert_backend_exception(cls, exception: Exception) -> ObjectId:
        """
        Save the name and stack trace of a python exception.
        """
        error_message = str(exception)
        stack_trace   = ''.join(traceback.format_exception(type(exception), exception, exception.__traceback__))
        
        error = ErrorEntry(
            timestamp     = now(),
            error_type    = "backend",
            error_message = error_message,
            stack_trace   = stack_trace,
        )

        result = await cls.errors.insert_one(error)
        return result.inserted_id

    @classmethod
    async def insert_frontend_exception(cls, error_message: str, stack_trace: str) -> ObjectId:
        """
        Save the name and stack trace of a frontend exception.
        """
        error = ErrorEntry(
            timestamp     = now(),
            error_type    = "frontend",
            error_message = error_message,
            stack_trace   = stack_trace,
        )

        result = await cls.errors.insert_one(error)
        return result.inserted_id

    @classmethod
    async def insert_error_message(cls, error_message: str) -> ObjectId:
        """
        Save an error message sent to the client without raising an exception.
        """
        error = ErrorEntry(
            timestamp     = now(),
            error_type    = "message",
            error_message = error_message,
        )

        result = await cls.errors.insert_one(error)
        return result.inserted_id

    @classmethod
    async def insert_bug_report(cls, description: str, contact: str) -> ObjectId:
        """
        Save a new manual bug report.
        """
        bug_report = BugReport(
            timestamp   = now(),
            description = description,
            contact     = contact,
            status      = "new",
        )

        result = await cls.bug_reports.insert_one(bug_report)
        return result.inserted_id