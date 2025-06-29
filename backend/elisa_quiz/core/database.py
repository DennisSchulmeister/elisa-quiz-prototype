# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import datetime, os, pymongo

mongodb_url = os.environ.get("MONGODB_URL", "mongodb://localhost:27071")
"""Connection string for the mongo database (read-only)"""

mongo_client = pymongo.AsyncMongoClient(mongodb_url)
"""Asynchronous mongo client"""

async def init_database():
    """
    Initialize database by creating missing indices.
    """
    await mongo_client.error_reports.errors.create_index(
        keys = [("timestamp", pymongo.ASCENDING)],
        expireAfterSeconds = 60 * 60 * 24 * int(os.environ.get("ERROR_REPORTS_TTL_DAYS", "365"))
    )

    #ANALYTICS_TTL_DAYS

def now() -> datetime.datetime:
    """
    Get the current date and time in UTC, as required by Mongo.
    """
    return datetime.datetime.now(tz=datetime.timezone.utc)