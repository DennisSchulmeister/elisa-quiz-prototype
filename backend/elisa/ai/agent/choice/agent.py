# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations
from typing     import TYPE_CHECKING

from ..base     import AgentBase

if TYPE_CHECKING:
    from ..types import Stateless

class ChoiceAgent(AgentBase[Stateless]):
    """
    Suggest and offer a choice of interactive activities.
    """
    code = "choice-agent"

    def __init__(self, **kwargs):
        super().__init__(state=Stateless(), **kwargs)
    
    activities = {
        "choice": "A menu with interactive activities to choose from",
    }