# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import datetime, os, pymongo

mongodb_url = os.environ.get("MONGODB_URL", "mongodb://localhost:27017")
"""Connection string for the mongo database (read-only)"""

mongo_client = pymongo.AsyncMongoClient(mongodb_url, tz_aware=True)
"""Asynchronous mongo client"""

def now() -> datetime.datetime:
    """
    Get the current date and time in UTC, as required by Mongo.
    """
    return datetime.datetime.now(tz=datetime.timezone.utc)