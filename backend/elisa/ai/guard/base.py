# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations
from abc        import ABC
from abc        import abstractmethod
from typing     import TYPE_CHECKING

from ...shared  import ReadConfigMixin

if TYPE_CHECKING:
    from ..assistant import AIAssistant
    from ..types     import UserChatMessage
    from .types      import GuardRailResult

class GuardRailBase(ABC, ReadConfigMixin):
    """
    Base class for guard rail implementations. Guard rails (there can multiple) check
    each new user message whether it is safe to accept. If a message is rejected e.g.
    due to size limitations or unsafe content a short explanation is returned.
    """

    def __init__(self, assistant: "AIAssistant"):
        """
        Constructor. Saves a reference to the top-level AI assistant, from which
        also the default LLM chat completion client can be accessed.
        """
        self._assistant = assistant
    
    @abstractmethod
    async def check_message(self, msg: "UserChatMessage") -> "GuardRailResult":
        """
        Inspect the given user message and decide whether it goes through or is rejected.
        """