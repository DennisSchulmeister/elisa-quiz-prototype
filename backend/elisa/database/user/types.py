# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__        import annotations
from bson              import ObjectId
from datetime          import datetime
from typing            import Literal
from pydantic          import BaseModel

from ...ai.agent.types import ActivityStates, AgentStates
from ...ai.guard.types import GuardRailResult
from ...ai.types       import ChatKey, ConversationMemory, MessageHistory, PersistenceStrategy, UserChatMessage

class Chat(ChatKey):
    """
    Chat conversation threads persisted on the server. This is just the combined
    long-term memory (full message history) and short-term memory (context memory)
    of a chat conversation.
    """
    _id:         ObjectId | None = None
    timestamp:   datetime
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
    timestamp: datetime
    thread_id: str
    title:     str

class ReviewLogEntry(BaseModel):
    """
    Log entry to document which action was taken when by whom during review of a
    flagged user message.
    """
    timestamp: datetime
    username:  str
    notes:     str

class FlaggedMessage(ChatKey):
    """
    Rejected user message flagged for manual review.
    """
    _id:        ObjectId | None = None
    timestamp:  datetime
    status:     Literal["needs_review", "false_positive", "reviewed"] = "needs_review"
    message:    UserChatMessage
    guard_rail: GuardRailResult
    review:     list[ReviewLogEntry]

class FlaggedMessageFilter(ChatKey):
    """
    Search filter for rejected user messages.
    """
    _id:    ObjectId | None = None
    status: Literal["needs_review", "false_positive", "reviewed"] = "needs_review"