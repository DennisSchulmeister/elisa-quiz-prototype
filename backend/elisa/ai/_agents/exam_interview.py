# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations
from pydantic   import BaseModel
from .._agent   import AgentBase

class ExamInterviewState(BaseModel):
    """
    Internal state of the exam interview agent.
    """

class ExamInterviewActivity(BaseModel):
    """
    Shared state of an interactive exam interview.
    """

class ExamInterviewAgent(AgentBase[ExamInterviewState]):
    """
    Suggest and offer a choice of interactive activities.
    """
    code = "exam-interview-agent"
    
    activities = {
        "exam-interview": "A menu with interactive activities to choose from",
    }

    def __init__(self, **kwargs):
        super().__init__(state=ExamInterviewState(), **kwargs)