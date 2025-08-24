# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations
from bson       import ObjectId
from datetime   import datetime
from pydantic   import BaseModel
from typing     import Literal, TYPE_CHECKING

from .shared    import mongo_client, now

if TYPE_CHECKING:
    from pymongo.asynchronous.collection import AsyncCollection
    from ..auth.user                     import User

class UserFeedbackData1(BaseModel):
    """
    Inner data of a fille-in user feedback survey (version 1).
    """
    survey_version:    Literal[1]
    star_rating:       int
    user_type:         Literal["student", "teacher", "other"]
    user_type_other:   str = ""
    edu_context:       Literal["primary", "secondary-1", "secondary-2", "vocational", "bachelor", "master", "other"]
    edu_context_other: str = ""
    learning_style:    Literal["supplied-materials", "guided", "independent"]
    wanted_features:   list[str]
    comment:           str

UserFeedbackData = UserFeedbackData1

class UserFeedback(BaseModel):
    """
    Anonymous user feedback via the built-in survey form. This helps us to
    understand the users and what features they wish.
    """
    _id:       ObjectId | None = None
    timestamp: datetime
    username:  str
    data:      UserFeedbackData

class UsageTime(BaseModel):
    """
    Anonymous time and duration of usage. This helps us to understand how
    often, when and how long the application is typically used.
    """
    _id:              ObjectId | None = None
    start_usage:      datetime
    end_usage:        datetime | None = None
    duration_seconds: int = -1

class LearningTopicBase(BaseModel):
    """
    Base-class for learning topic data, as recognized by the LLM.
    """
    category:     str
    sub_category: str
    topic:        str

class LearningTopic(LearningTopicBase):
    """
    Anonymous keyword of learned topic. This helps us to understand what
    content users typically want to learn with the application.
    """
    _id:   ObjectId | None = None
    count: int

class AnalyticsDatabase:
    """
    Database for anonymous usage statistics and anonymous user feedback
    """
    db = mongo_client.analytics
    """Mongo database instance"""

    user_feedbacks: AsyncCollection = mongo_client.analytics.user_feedbacks
    """Anonymous user feedback via the built-in survey form"""

    usage_times: AsyncCollection = mongo_client.analytics.usage_times
    """Anonymous time and duration of usage"""

    learning_topics: AsyncCollection = mongo_client.analytics.learning_topics
    """Anonymous keyword of learned topic"""

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