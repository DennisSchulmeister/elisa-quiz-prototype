# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from ..base import AgentBase
from ..base import PersonaBase
from .types import DefaultState

class DefaultAgent(AgentBase[DefaultState]):
    """
    Default agent that responds to all chat messages not targeted at a more specialized agent.
    """
    code  = "default-agent"

    def __init__(self, **kwargs):
        super().__init__(state=DefaultState(), **kwargs)

    def greet_user(self):
        """
        Say hello to the user to initiate the conversation, if not already done.
        """
        if not self._state.welcome_done:
            # Say "Hi!" to the LLM and stream back response
            pass            

class WelcomePersona(PersonaBase):
    """
    Specialized persona to welcome the user at the start of the conversation.
    """

class DefaultPersona(PersonaBase):
    """
    Default persona after the welcome procedure.
    """