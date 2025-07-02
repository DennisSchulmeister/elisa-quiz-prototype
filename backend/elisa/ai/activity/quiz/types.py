# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from typing import TypedDict

class QuizQuestion(TypedDict):
    """
    Question type for the quiz activity.
    """
    question: str
    """Question text"""

    answers: list[str]
    """Possible answers"""

    correct: int
    """Index of correct answer"""

class QuizActivity(TypedDict):
    """
    Quiz activity where each question has a text and several answers of which
    exactly one is correct.
    """
    subject: str
    """Quiz subject"""

    level: str
    """Difficulty level"""

    questions: list[QuizQuestion]
    """Quiz questions"""

    given_answers: list[int]
    """Answers from users (index of the answer in same order as the questions)"""