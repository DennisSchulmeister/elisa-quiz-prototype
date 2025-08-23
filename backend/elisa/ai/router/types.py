# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from pydantic import BaseModel
from pydantic import Field

class ChooseAgentResult(BaseModel):
    """
    Agent which should handle a received user chat message.
    """
    agent_code: str | None = Field(
        description = "Chosen agent to handle the user message"
    )

    question: str | None = Field(
        description = "Question to the user in case multiple agents are suitable"
    )