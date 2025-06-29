# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import datetime

from bson                            import ObjectId
from typeguard                       import check_type
from typing                          import Literal
from typing                          import NotRequired
from typing                          import TypedDict
from pymongo.asynchronous.collection import AsyncCollection

from ..core.database                 import mongo_client
from ..core.database                 import now

# class Error(TypedDict):
#     """
#     Error or crash report that helps to analyze and fix bugs that occurred
#     in production.
#     """
#     _id:           NotRequired[ObjectId]
#     timestamp:     datetime.datetime
#     error_type:    Literal["backend", "frontend", "message"]
#     error_message: str
#     stack_trace:   str

class UserDatabase:
    """
    Database for regular user data
    """
    db = mongo_client.users
    """Mongo database instance"""

    # errors: AsyncCollection[ErrorEntry] = mongo_client.error_reports.errors
    # """Error collection"""