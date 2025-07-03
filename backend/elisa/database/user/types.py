# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import datetime

from bson        import ObjectId
from pydantic    import BaseModel

from ...ai.types import LongTermMemory
from ...ai.types import ShortTermMemory

class ChatHistory(BaseModel):
    """
    Chat conversation threads persisted on the server. This is just the combined
    long-term memory (full message history) and short-term memory (context memory)
    of a chat conversation.
    """
    _id:        ObjectId | None = None
    timestamp:  datetime.datetime
    username:   str
    encrypt:    bool
    long_term:  LongTermMemory
    short_term: ShortTermMemory