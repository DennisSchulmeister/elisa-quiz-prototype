# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations

from pydantic import BaseModel
from typing   import TYPE_CHECKING

if TYPE_CHECKING:
    from bson     import ObjectId
    from datetime import datetime
    from typing   import Literal

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