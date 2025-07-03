# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from bson                            import ObjectId
from pymongo.asynchronous.collection import AsyncCollection

from ...ai.types                     import MemoryTransaction
from ...database.utils               import now
from ..utils                         import mongo_client
from .types                          import ChatHistory

class UserDatabase:
    """
    Database for regular user data like chat memory etc.
    """
    db = mongo_client.user
    """Mongo database instance"""

    chat_history: AsyncCollection = mongo_client.user.chat_history
    """Anonymous user feedback via the built-in survey form."""

    @classmethod
    async def get_chat_history(cls, username: str, thread_id: str) -> ChatHistory | None:
        """
        Read persisted chat history of an old conversation. Either returns the found
        database entry (containing the short-term and long-term memory) or `None`, if
        no history has been saved.

        Note: This version does not yet support encryption!
        """
        return await cls.chat_history.find_one({
            "username": username,
            "long_term": {
                "thread_id": thread_id
            }
        })

    @classmethod
    async def apply_memory_transaction(cls, username: str, tx: MemoryTransaction) -> ObjectId:
        """
        Apply changes of the given memory transaction to the database. This either creates
        a new chat history entry, if it doesn't exist, or updates the existing entry.

        Note: This version does not yet support encryption!
        """
        object_id = await cls.chat_history.find_one(
            filter = {
                "username": username,
                "long_term": {
                    "thread_id": tx.thread_id,
                }
            },
            projection = ["_id"],
        )

        if not object_id:
            object_id = (await cls.chat_history.insert_one({
                "timestamp": now(),
                "username":  username,
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
            await cls.chat_history.update_one({"_id": object_id}, {
                "$set": {
                    "timestamp": now(),
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