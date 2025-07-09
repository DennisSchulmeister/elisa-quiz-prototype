# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from .choice.agent         import ChoiceAgent
from .default.agent        import DefaultAgent
from .exam_interview.agent import ExamInterviewAgent
from .quiz.agent           import QuizAgent

agents = [
    ChoiceAgent,
    DefaultAgent,
    ExamInterviewAgent,
    QuizAgent,
]
"""All agent classes known to the top-level chat manager"""