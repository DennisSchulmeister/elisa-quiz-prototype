# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations
from pydantic   import BaseModel, Field

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
