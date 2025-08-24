# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations
from pydantic   import BaseModel
from typing     import TYPE_CHECKING

from .._agent   import AgentBase

if TYPE_CHECKING:
    from .._agent import Stateless

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

class ChoiceAgent(AgentBase[Stateless]):
    """
    Suggest and offer a choice of interactive activities.
    """
    code = "choice-agent"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    activities = {
        "choice": "A menu with interactive activities to choose from",
    }