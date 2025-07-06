# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from ..base import AgentBase
from .types import QuizActivity

class QuizAgent(AgentBase):
    """
    Play a quiz with multiple choice questions to test the user's level of knowledge.
    """
    code = "quiz-agent"
    
    activities = {
        "quiz": "A fun multiple choice quiz where the player must pick the correct answer from four choices",
    }