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

class SummarizerBase(ABC, ReadConfigMixin):
    """
    Base class for conversation summarizer implementations. The conversation summarizer
    (there can only be one per conversation) compresses the message history to save bandwidth
    and tokens when providing past messages as context to the LLM.
    """

    keep_count = -1
    """Number of recent messages kept verbatim before summarizing"""

    def __init__(self, assistant: "AIAssistant"):
        """
        Constructor. Saves a reference to the top-level AI assistant, from which
        also the default LLM chat completion client can be accessed.
        """
        self._assistant = assistant
    
    @abstractmethod
    async def compress_memory(self):
        """
        Summarize older messages in the conversation memory and remove them from the
        recent messages list.
        """