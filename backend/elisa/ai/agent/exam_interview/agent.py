# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from ..base import AgentBase
from .types import ExamInterviewActivity
from .types import ExamInterviewState

class ExamInterviewAgent(AgentBase):
    """
    Suggest and offer a choice of interactive activities.
    """
    code = "exam-interview-agent"
    
    activities = {
        "exam-interview": "A menu with interactive activities to choose from",
    }