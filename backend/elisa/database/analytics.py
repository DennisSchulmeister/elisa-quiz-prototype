# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import datetime

from bson                            import ObjectId
from typeguard                       import check_type
from typing                          import Literal
from typing                          import NotRequired
from typing                          import TypedDict
from pymongo.asynchronous.collection import AsyncCollection

from ..core.database                 import mongo_client
from ..core.database                 import now

class UserFeedback(TypedDict):
    """
    Anonymous user feedback via the built-in survey form. This helps us to
    understand the users and what features they wish.
    """
    _id:             NotRequired[ObjectId]
    timestamp:       datetime.datetime
    user_type:       Literal["student", "teacher", "other"]
    star_rating:     int
    wanted_features: list[str]
    comment:         str

class UsageTime(TypedDict):
    """
    Anonymous time and duration of usage. This helps us to understand how
    often, when and how long the application is typically used.
    """
    _id:              NotRequired[ObjectId]
    start_usage:      datetime.datetime
    end_usage:        NotRequired[datetime.datetime]
    duration_seconds: NotRequired[int]

class LearningTopic(TypedDict):
    """
    Anonymous keyword of learned topic. This helps us to understand what
    content users typically want to learn with the application.
    """
    _id:     NotRequired[ObjectId]
    keyword: str
    count:   int

class AnalyticsDatabase:
    """
    Database for anonymous usage statistics and anonymous user feedback
    """
    db = mongo_client.analytics
    """Mongo database instance"""

    user_feedbacks: AsyncCollection[UserFeedback] = mongo_client.analytics.user_feedbacks
    """Anonymous user feedback via the built-in survey form."""

    usage_times: AsyncCollection[UsageTime] = mongo_client.analytics.usage_times
    """Anonymous time and duration of usage."""

    learning_topics: AsyncCollection[LearningTopic] = mongo_client.analytics.learning_topics
    """Anonymous keyword of learned topic."""

    @classmethod
    async def save_user_feedback(cls, feedback: UserFeedback) -> ObjectId:
        """
        Save a new anonymous user feedback.
        """
        check_type(feedback, UserFeedback)
        result = await cls.user_feedbacks.insert_one(feedback)
        return result.inserted_id
    
    @classmethod
    async def save_usage_start(cls) -> ObjectId:
        """
        Create a new usage time entry to record the start of application usage by
        an anonymous user.
        """
        usage_time = UsageTime(start_usage=now())
        result = await cls.usage_times.insert_one(usage_time)
        return result.inserted_id
    
    @classmethod
    async def save_usage_end(cls, object_id: ObjectId) -> ObjectId|None:
        """
        Update an existing usage time entry to record the end and duration of
        application usage by an anonymous user. Does nothing and returns `None`,
        if no usage time entry with the given Id can be found.
        """
        usage_time = await cls.usage_times.find_one({"_id": object_id})

        if not usage_time:
            return
        
        usage_time["end_usage"] = now()
        usage_time["duration_seconds"] = int((usage_time["end_usage"] - usage_time["start_usage"]).total_seconds())

        await cls.usage_times.replace_one({"_id": object_id}, usage_time)
        return object_id

    @classmethod
    async def delete_usage_time(cls, object_id: ObjectId):
        """
        Delete usage time entry with the given Id. Does nothing, if the entry
        cannot be found.
        """
        await cls.usage_times.delete_one({"_id": object_id})

    @classmethod
    async def add_learning_topic(cls, keyword: str):
        """
        Create a new learning topic or increase its count, if it already exists.
        """
        await cls.learning_topics.update_one(
            {"keyword": keyword.lower()},
            {"$inc": {"count": 1}},
            upsert = True,
        )