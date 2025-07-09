# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import datetime

from bson              import ObjectId
from pydantic          import BaseModel

from ...ai.agent.types import ActivityStates
from ...ai.agent.types import AgentStates
from ...ai.types       import ChatKey
from ...ai.types       import ConversationMemory
from ...ai.types       import MessageHistory
from ...ai.types       import PersistenceStrategy

class Chat(ChatKey):
    """
    Chat conversation threads persisted on the server. This is just the combined
    long-term memory (full message history) and short-term memory (context memory)
    of a chat conversation.
    """
    _id:         ObjectId | None = None
    timestamp:   datetime.datetime
    title:       str
    persistence: PersistenceStrategy
    encrypt:     bool
    history:     MessageHistory
    memory:      ConversationMemory
    agents:      AgentStates
    activities:  ActivityStates

class ChatShort(BaseModel):
    """
    Reduced dataset for getting a list of all saved chat conversations of the user.
    """
    timestamp: datetime.datetime
    thread_id: str
    title:     str
