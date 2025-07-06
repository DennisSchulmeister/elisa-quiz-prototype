# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from bson                            import ObjectId
from pydantic                        import ValidationError
from pymongo.asynchronous.collection import AsyncCollection

from ...ai.types                     import MemoryUpdate
from ...database.utils               import now
from ..utils                         import mongo_client
from .types                          import Chat
from .types                          import ChatShort

class UserDatabase:
    """
    Database for regular user data like chat memory etc.
    """
    db = mongo_client.user
    """Mongo database instance"""

    chats: AsyncCollection = mongo_client.user.chats
    """Anonymous user feedback via the built-in survey form."""

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
            projection = ["_id", "timestamp", "title", "long_term.thread_id"],
        ):
            try:
                chat = ChatShort(
                    timestamp = chat_doc["timestamp"],
                    thread_id = chat_doc["long_term"]["thread_id"],
                    title     = chat_doc["title"]
                )

                result.append(ChatShort.model_validate(chat))
            except (KeyError, ValidationError):
                pass

        return result

    @classmethod
    async def get_chat(cls, username: str, thread_id: str) -> Chat | None:
        """
        Read persisted chat history of an old conversation. Either returns the found
        database entry (containing the short-term and long-term memory) or `None`, if
        no history has been saved.

        Note: This version does not yet support encryption!
        """
        chat = await cls.chats.find_one({
            "username": username,
            "long_term": {
                "thread_id": thread_id
            }
        })

        try:
            return Chat.model_validate(chat)
        except ValidationError:
            return None

    @classmethod
    async def rename_chat(cls, username: str, thread_id: str, title: str):
        """
        Change title of a chat conversation.
        """
        await cls.chats.update_one({
            "username": username,
            "long_term": {
                "thread_id": thread_id,
            }
        }, {
            "title": title,
        });

    @classmethod
    async def save_chat(cls, chat: Chat):
        """
        Save a full chat entry, usually because it was previously persisted on the client,
        but shall now be managed by the server.
        """
        object_id = await cls.chats.find_one(
            filter = {
                "username": chat.username,
                "long_term": {
                    "thread_id": chat.long_term.thread_id
                }

            },
            projection = ["_id"],
        )

        if not object_id:
            await cls.chats.insert_one({
                "username":   chat.username,
                "timestamp":  chat.timestamp,
                "title":      chat.title,
                "encrypt":    chat.encrypt,
                "long_term":  chat.long_term,
                "short_term": chat.short_term,
            })
        else:
            await cls.chats.update_one({"_id": object_id}, {
                "username":   chat.username,
                "timestamp":  chat.timestamp,
                "title":      chat.title,
                "encrypt":    chat.encrypt,
                "long_term":  chat.long_term,
                "short_term": chat.short_term,
            })

    @classmethod
    async def delete_chat(cls, username: str, thread_id: str):
        """
        Delete chat history of an old conversation, if it exists.
        """
        await cls.chats.delete_one({
            "username": username,
            "long_term": {
                "thread_id": thread_id
            }
        })
    
    @classmethod
    async def apply_memory_update(cls, username: str, tx: MemoryUpdate) -> ObjectId:
        """
        Apply changes of the given memory update to the database. This either creates
        a new chat history entry, if it doesn't exist, or updates the existing entry.

        Note: This version does not yet support encryption!
        """
        object_id = await cls.chats.find_one(
            filter = {
                "username": username,
                "long_term": {
                    "thread_id": tx.thread_id,
                }
            },
            projection = ["_id"],
        )

        if not object_id:
            object_id = (await cls.chats.insert_one({
                "username":  username,
                "timestamp": now(),
                "title":     tx.title,
                "encrypt":   False,
                "long_term": {
                    "thread_id": tx.thread_id,
                    "messages":  tx.new_messages,
                },
                "short_term": {
                    "messages": tx.new_messages[-tx.short_term_n:],
                    "previous": tx.previous,
                },
            })).inserted_id
        else:
            await cls.chats.update_one({"_id": object_id}, {
                "$set": {
                    "timestamp": now(),
                    "title": tx.title,
                    "short_term.previous": tx.previous,
                },
                "$push": {
                    "long_term.messages": {
                        "$each": tx.new_messages,
                    },
                    "short_term.messages": {
                        "$each":  tx.new_messages,
                        "$slice": -tx.short_term_n,
                    }
                },
            })

        return object_id