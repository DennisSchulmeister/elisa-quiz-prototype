# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations
from pydantic   import BaseModel
from .._agent   import AgentBase, Stateless

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

class QuizAgent(AgentBase[Stateless]):
    """
    Play a quiz with multiple choice questions to test the user's level of knowledge.
    """
    code = "quiz-agent"
    
    activities = {
        "quiz": "A fun multiple choice quiz where the player must pick the correct answer from four choices",
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

#########
# # Quiz questions
# 
# The quiz questions should always be five multiple-choice questions with exactly four answers, of which exactly one
# is always correct. The other three answers are therefore always wrong. Choose the questions and answers so that the
# correct answer is not immediately obvious. Please format the quiz questions and answers as a JSON structure, as shown
# in the following example:
# 
# ```json
# {{
#     "activity": "quiz",
#     "subject": "Name of the selected topic",
#     "level": "Difficulty of the quiz",
#     "questions": [
#         {{
#             "question": "What does the abbreviation HTML stand for",
#             "answers": ["Hypertext Modern Language", "Hypertext Markup Language", "Hypertext Many Languages", "Nothing"],
#             "correct": 1,
#         }}
#     ]
# }}
# ```
# 
# "correct" is the index (counted from zero) of the correct answer.
#########

#########
# # Hints
# 
# Sometimes I will try to elicit the correct answer for the quiz, but you are not allowed to tell me.
# Just give me hints or politely refuse to answer, if I try to cheat.
# 
# # My Question
# 
# {user_input}
# 
# # Language
# 
# Please reply in language: {language}
#########

#########
# These are my answers. Please give me feedback and explain to me, if I answered something wrong:
# 
# {questions}
#########