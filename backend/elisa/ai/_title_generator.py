# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations
from abc        import ABC, abstractmethod
from pydantic   import BaseModel, Field
from typing     import TYPE_CHECKING

from ..shared   import ReadConfigMixin

if TYPE_CHECKING:
    from .assistant import AIAssistant

class ChatTitle(BaseModel):
    """
    Distilled title of the chat conversation so far.
    """
    meaningful: bool = Field(
        description = "Whether the conversation already allows to distill a descriptive title",
    )

    title: str = Field(
        description = "Clear, concise, and informative title for the conversation",
    )

class TitleGeneratorBase(ABC, ReadConfigMixin):
    """
    Base class for title generator implementations. The title generator (there can only
    be one per conversation) monitors new chat conversations and suggests a title once
    enough messages have been seen.
    """

    def __init__(self, assistant: AIAssistant):
        """
        Constructor. Saves a reference to the top-level AI assistant, from which
        also the default LLM chat completion client can be accessed.
        """
        self._assistant = assistant

    @abstractmethod
    async def suggest_title(self) -> ChatTitle:
        """
        Inspect the conversation memory saved in the AI assistant's state and try to
        suggest a meaningful title under which to save the conversation. Will be called
        every time a new message as added for as long as no title has been found, which
        is signaled by a flag in the response type.
        """