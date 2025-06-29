# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import datetime, traceback

from bson                            import ObjectId
from typeguard                       import check_type
from typing                          import Literal
from typing                          import NotRequired
from typing                          import TypedDict
from pymongo.asynchronous.collection import AsyncCollection

from ..core.database                 import mongo_client
from ..core.database                 import now

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

class ErrorDatabase:
    """
    Database for crash reports and stack traces
    """
    db = mongo_client.error_reports
    """Mongo database instance"""

    errors: AsyncCollection[ErrorEntry] = mongo_client.error_reports.errors
    """Error collection"""

    @classmethod
    async def save_backend_exception(cls, exception: Exception) -> ObjectId:
        """
        Save the name and stack trace of a python exception.
        """
        check_type(exception, Exception)
        
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
    async def save_frontend_exception(cls, error_message: str, stack_trace: str) -> ObjectId:
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
    async def save_error_message(cls, error_message: str) -> ObjectId:
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