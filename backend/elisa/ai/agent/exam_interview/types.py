# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from pydantic import BaseModel

class ExamInterviewState(BaseModel):
    """
    Internal state of the exam interview agent.
    """

class ExamInterviewActivity(BaseModel):
    """
    Shared state of an interactive exam interview.
    """