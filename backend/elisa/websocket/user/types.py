# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import datetime

from pydantic    import BaseModel
from ...ai.types import LongTermMemory
from ...ai.types import ShortTermMemory

class ChatKey(BaseModel):
    """
    Key values (besides username) to address a persisted chat.
    """
    thread_id: str

class RenameChat(BaseModel):
    """
    Message body to change the title of a chat conversation.
    """
    thread_id: str
    title:     str

class SaveChat(BaseModel):
    """
    Message body to move a full chat conversation from client to server,
    so that it is centrally saved on the server.
    """
    timestamp:  datetime.datetime
    title:      str
    encrypt:    bool
    long_term:  LongTermMemory
    short_term: ShortTermMemory