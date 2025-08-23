# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations

import datetime

from pydantic          import BaseModel

from ...ai.agent.types import ActivityStates
from ...ai.agent.types import AgentStates
from ...ai.types       import ChatKey
from ...ai.types       import ConversationMemory
from ...ai.types       import MessageHistory
from ...ai.types       import PersistenceStrategy

class RenameChat(ChatKey):
    """
    Message body to change the title of a chat conversation.
    """
    title: str

class SaveChat(BaseModel):
    """
    Message body to move a full chat conversation from client to server,
    so that it is centrally saved on the server.
    """
    timestamp:   datetime.datetime
    title:       str
    persistence: PersistenceStrategy
    encrypt:     bool
    history:     MessageHistory
    memory:      ConversationMemory
    agents:      AgentStates
    activities:  ActivityStates
