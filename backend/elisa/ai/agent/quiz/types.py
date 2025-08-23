# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations
from pydantic   import BaseModel

class QuizQuestion(BaseModel):
    """
    Question type for the quiz activity.
    """
    question: str
    answers:  list[str]
    correct:  int

class QuizActivity(BaseModel):
    """
    Quiz activity where each question has a text and several answers of which
    exactly one is correct.
    """
    subject:       str
    level:         str
    questions:     list[QuizQuestion]
    given_answers: list[int] = []