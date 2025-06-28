# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import os
from pymongo import AsyncMongoClient

mongodb_url = os.environ.get("MONGODB_URL", "mongodb://localhost:27071")
"""Connection string for the mongo database (read-only)"""

mongo_client = AsyncMongoClient(mongodb_url)
"""Asynchronous mongo client"""
