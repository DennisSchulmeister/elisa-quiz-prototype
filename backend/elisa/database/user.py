# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__       import annotations
from bson             import ObjectId
from datetime         import datetime
from typing           import Literal, TYPE_CHECKING
from pydantic         import BaseModel, ValidationError

from ..ai.models      import ActivityStates, AgentStates, ChatKey, ConversationMemory, GuardRailResult
from ..ai.models      import MessageHistory, PersistenceStrategy, UserChatMessage
from .shared          import now
from .shared          import mongo_client

if TYPE_CHECKING:
    from pymongo.asynchronous.collection import AsyncCollection

    from ..ai._guard_rail                import GuardRailResult
    from ..ai.models                     import ActivityUpdate, AgentUpdate, MemoryUpdate, UserChatMessage

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

class UserDatabase:
    """
    Database for regular user data like chat memory etc.
    """
    db = mongo_client.user
    """Mongo database instance"""

    chats: AsyncCollection = mongo_client.user.chats
    """Chat conversations"""

    flagged_messages: AsyncCollection = mongo_client.user.flagged_messages
    """Critical chat messages flagged for manual review"""

    @classmethod
    async def get_chats(cls, username: str) -> list[ChatShort]:
        """
        Read an overview list of all saved chat conversations of the user. Only returns
        the key values and the title of each chat.
        """
        result = []

        async for chat_doc in cls.chats.find(
            filter = {
                "username": username,
            },
            projection = ["_id", "thread_id", "timestamp", "title"],
        ):
            try:
                chat = ChatShort(
                    timestamp = chat_doc["timestamp"],
                    thread_id = chat_doc["thread_id"],
                    title     = chat_doc["title"]
                )

                result.append(ChatShort.model_validate(chat))
            except (KeyError, ValidationError):
                pass

        return result

    @classmethod
    async def get_chat(cls, key: ChatKey) -> Chat | None:
        """
        Read persisted chat history of an old conversation. Either returns the found
        database entry (containing the short-term and long-term memory) or `None`, if
        no history has been saved.

        Note: This version does not yet support encryption!
        """
        chat = await cls.chats.find_one({
            "username":  key.username,
            "thread_id": key.thread_id,
        })

        try:
            return Chat.model_validate(chat)
        except ValidationError:
            return None

    @classmethod
    async def rename_chat(cls, key: ChatKey, title: str):
        """
        Change title of a chat conversation.
        """
        await cls.chats.update_one({
            "username":  key.username,
            "thread_id": key.thread_id,
        }, {
            "title": title,
        });

    @classmethod
    async def save_chat(cls, chat: Chat):
        """
        Save a full chat entry using upsert logic. If a chat with the same username and
        thread id already exists on the database, it will be overwritten. Otherwise a new
        chat document will be created.
        """
        object_id = await cls.chats.find_one(
            filter = {
                "username": chat.username,
                "thread_id": chat.thread_id,

            },
            projection = ["_id"],
        )

        if not object_id:
            await cls.chats.insert_one({
                "username":    chat.username,
                "thread_id":   chat.thread_id,
                "timestamp":   chat.timestamp,
                "title":       chat.title,
                "persistence": chat.persistence,
                "encrypt":     chat.encrypt,
                "history":     chat.history,
                "memory":      chat.memory,
                "agents":      chat.agents,
                "activities":  chat.activities,
            })
        else:
            await cls.chats.update_one({"_id": object_id}, {
                "username":    chat.username,
                "thread_id":   chat.thread_id,
                "timestamp":   chat.timestamp,
                "title":       chat.title,
                "persistence": chat.persistence,
                "encrypt":     chat.encrypt,
                "history":     chat.history,
                "memory":      chat.memory,
                "agents":      chat.agents,
                "activities":  chat.activities,
            })

    @classmethod
    async def delete_chat(cls, key: ChatKey):
        """
        Delete chat history of an old conversation, if it exists.
        """
        await cls.chats.delete_one({
            "username":  key.username,
            "thread_id": key.thread_id,
        })
    
    @classmethod
    async def get_flagged_messages(cls, filter: FlaggedMessageFilter) -> list[FlaggedMessage]:
        """
        Get messages flagged for manual review.
        """
        result = []

        async for flagged_message in cls.flagged_messages.find(
            filter = {
                "_id":       filter._id,
                "username":  filter.username,
                "thread_id": filter.thread_id,
                "status":    filter.status,
            },
        ):
            try:
                result.append(FlaggedMessage.model_validate(flagged_message))
            except ValidationError:
                pass

        return result
    
    @classmethod
    async def insert_flagged_message(cls, chat: ChatKey, msg: UserChatMessage, guard_rail: GuardRailResult):
        """
        Insert a new user message flagged for manual review.
        """
        await cls.flagged_messages.insert_one({
            "username":   chat.username,
            "thread_id":  chat.thread_id,
            "timestamp":  now(),
            "status":     "needs_review",
            "message":    msg.model_dump(),
            "guard_rail": guard_rail.model_dump(),
            "review":     [],
        })

    @classmethod
    async def save_flagged_message(cls, msg: FlaggedMessage):
        """
        Save or update a message flagged for manual review.
        """
        if not msg._id:
            await cls.flagged_messages.insert_one(msg.model_dump())
        else:
            await cls.flagged_messages.update_one({"_id": msg._id}, msg.model_dump())
    
    @classmethod
    async def delete_flagged_message(cls, id: ObjectId):
        """
        Delete a flagged message, if it exists.
        """
        await cls.flagged_messages.delete_one({"_id": id})
    
    @classmethod
    async def apply_memory_update(cls, key: ChatKey, update: MemoryUpdate) -> ObjectId | None:
        """
        Update the conversational memory in the database. The chat must already exist.
        """
        object_id = await cls.chats.find_one(
            filter = {
                "username":  key.username,
                "thread_id": key.thread_id,
            },
            projection = ["_id"],
        )

        if object_id:
            await cls.chats.update_one({"_id": object_id}, {
                "$set": {
                    "timestamp": now(),
                    "title": update.chat_title,
                    "short_term.previous": update.previous,
                },
                "$push": {
                    "history.messages": {
                        "$each": update.new_messages,
                    },
                    "memory.messages": {
                        "$each":  update.new_messages,
                        "$slice": -update.keep_count,
                    }
                },
            })

        return object_id
    
    @classmethod
    async def apply_agent_update(cls, key: ChatKey, update: AgentUpdate) -> ObjectId | None:
        """
        Update the agent state in the database. The chat must already exist.
        """
        object_id = await cls.chats.find_one(
            filter = {
                "username":  key.username,
                "thread_id": key.thread_id,
            },
            projection = ["_id"],
        )

        if object_id:
            await cls.chats.update_one(
                {"_id": object_id},
                {"$set": {"agents." + mongo_path(update.agent, update.path): update.value}
            })

        return object_id

    @classmethod
    async def apply_activity_update(cls, key: ChatKey, update: ActivityUpdate) -> ObjectId | None:
        """
        Update the activity state in the database. The chat must already exist.
        """
        object_id = await cls.chats.find_one(
            filter = {
                "username":  key.username,
                "thread_id": key.thread_id,
            },
            projection = ["_id"],
        )

        if object_id:
            await cls.chats.update_one(
                {"_id": object_id},
                {"$set": {"activities." + mongo_path(update.id, update.path): update.value}
            })

        return object_id

def mongo_path(key: str, path: str) -> str:
    """
    Convert the internal path notation to mongo notation. The difference lies
    in the indexing of arrays. Mongo uses dot-notation there, too. Internally
    we use traditional square-bracket notation.
    """
    if path:
        return key + "." + path.replace("[", ".").replace("]", ".")
    else:
        return key