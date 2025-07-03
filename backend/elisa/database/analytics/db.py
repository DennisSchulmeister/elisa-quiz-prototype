# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from bson                            import ObjectId
from pymongo.asynchronous.collection import AsyncCollection

from ...auth.user                    import User
from ..utils                         import mongo_client
from ..utils                         import now
from .types                          import LearningTopicBase
from .types                          import UsageTime
from .types                          import UserFeedback
from .types                          import UserFeedbackData

class AnalyticsDatabase:
    """
    Database for anonymous usage statistics and anonymous user feedback
    """
    db = mongo_client.analytics
    """Mongo database instance"""

    user_feedbacks: AsyncCollection = mongo_client.analytics.user_feedbacks
    """Anonymous user feedback via the built-in survey form."""

    usage_times: AsyncCollection = mongo_client.analytics.usage_times
    """Anonymous time and duration of usage."""

    learning_topics: AsyncCollection = mongo_client.analytics.learning_topics
    """Anonymous keyword of learned topic."""

    @classmethod
    async def insert_user_feedback(cls, feedback_data: UserFeedbackData, user: User) -> ObjectId:
        """
        Save a new anonymous user feedback.
        """
        feedback = UserFeedback(timestamp=now(), username=user.subject, data=feedback_data)
        result = await cls.user_feedbacks.insert_one(feedback.model_dump())
        return result.inserted_id
    
    @classmethod
    async def save_usage_start(cls, usage_time: UsageTime|None = None) -> ObjectId:
        """
        Create a new usage time entry to record the start of application usage by
        an anonymous user.
        """
        if usage_time is None:
            usage_time = UsageTime(start_usage=now())

        result = await cls.usage_times.insert_one(usage_time.model_dump())
        return result.inserted_id
    
    @classmethod
    async def save_usage_end(cls, object_id: ObjectId) -> ObjectId|None:
        """
        Update an existing usage time entry to record the end and duration of
        application usage by an anonymous user. Does nothing and returns `None`,
        if no usage time entry with the given Id can be found.
        """
        _usage_time = await cls.usage_times.find_one({"_id": object_id})

        if not _usage_time:
            return
        
        usage_time = UsageTime(**_usage_time)
        usage_time.end_usage = now()
        usage_time.duration_seconds = int((usage_time.end_usage - usage_time.start_usage).total_seconds())
        
        await cls.usage_times.replace_one({"_id": object_id}, usage_time.model_dump())
        return object_id

    @classmethod
    async def delete_usage_time(cls, object_id: ObjectId):
        """
        Delete usage time entry with the given Id. Does nothing, if the entry
        cannot be found.
        """
        await cls.usage_times.delete_one({"_id": object_id})

    @classmethod
    async def upsert_learning_topic(cls, learning_topic: LearningTopicBase):
        """
        Create a new learning topic or increase its count, if it already exists.
        """
        await cls.learning_topics.update_one(
            learning_topic.model_dump(),
            {"$inc": {"count": 1}},
            upsert = True,
        )