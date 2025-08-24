# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations
from bson       import ObjectId
from datetime   import datetime
from pydantic   import BaseModel
from traceback  import format_exception
from typing     import Literal, TYPE_CHECKING

from .shared    import mongo_client, now

if TYPE_CHECKING:
    from pymongo.asynchronous.collection import AsyncCollection

class ErrorEntry(BaseModel):
    """
    Error or crash report that helps to analyze and fix bugs that occurred
    in production.
    """
    _id:           ObjectId | None = None
    timestamp:     datetime
    error_type:    Literal["server", "client", "message"]
    error_message: str
    stack_trace:   str = ""

class BugReport(BaseModel):
    """
    Manual bug report filled-in within the client.
    """
    _id:         ObjectId | None = None
    timestamp:   datetime
    username:    str
    description: str
    contact:     str
    status:      Literal["new", "in-progress", "resolved", "works-for-me", "wont-fix"]

class ErrorDatabase:
    """
    Database for crash reports and stack traces
    """
    db = mongo_client.error
    """Mongo database instance"""

    errors: AsyncCollection = mongo_client.error.errors
    """Error collection"""

    bug_reports: AsyncCollection = mongo_client.error.bug_reports
    """Manual bug reports"""

    @classmethod
    async def insert_server_exception(cls, exception: Exception) -> ObjectId:
        """
        Save the name and stack trace of a python exception.
        """
        error_message = str(exception)
        stack_trace   = ''.join(format_exception(type(exception), exception, exception.__traceback__))

        error = ErrorEntry(
            timestamp     = now(),
            error_type    = "server",
            error_message = error_message,
            stack_trace   = stack_trace,
        )

        result = await cls.errors.insert_one(error.model_dump())
        return result.inserted_id

    @classmethod
    async def insert_client_exception(cls, error_message: str, stack_trace: str) -> ObjectId:
        """
        Save the name and stack trace of a client exception.
        """
        error = ErrorEntry(
            timestamp     = now(),
            error_type    = "client",
            error_message = error_message,
            stack_trace   = stack_trace,
        )

        result = await cls.errors.insert_one(error.model_dump())
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

        result = await cls.errors.insert_one(error.model_dump())
        return result.inserted_id

    @classmethod
    async def insert_bug_report(cls, username: str, description: str, contact: str) -> ObjectId:
        """
        Save a new manual bug report.
        """
        bug_report = BugReport(
            timestamp   = now(),
            username    = username,
            description = description,
            contact     = contact,
            status      = "new",
        )

        result = await cls.bug_reports.insert_one(bug_report.model_dump())
        return result.inserted_id