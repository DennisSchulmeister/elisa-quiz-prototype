# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from ..utils import mongo_client

class UserDatabase:
    """
    Database for regular user data like chat memory etc.
    """
    db = mongo_client.user
    """Mongo database instance"""