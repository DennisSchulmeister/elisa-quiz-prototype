# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from pydantic import BaseModel

class Choice(BaseModel):
    """
    A single menu choice.
    """
    activity:    str
    description: str

class ChoiceActivity(BaseModel):
    """
    Activity where the user can choose other activities from a menu.
    """
    choices: list[Choice] = []