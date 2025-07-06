# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from .choice.agent         import ChoiceAgent
from .exam_interview.agent import ExamInterviewAgent
from .quiz.agent           import QuizAgent
from .welcome.agent        import WelcomeAgent

agents = [
    ChoiceAgent,
    ExamInterviewAgent,
    QuizAgent,
    WelcomeAgent,
]
"""All agent classes known to the top-level chat manager"""