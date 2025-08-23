# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations
from pydantic   import BaseModel
from pydantic   import Field
from typing     import Literal

CheckResult = Literal["accept", "reject-warning", "reject-critical"]

class Explanation(BaseModel):
    """
    Short text explanation
    """
    text: str = Field(
        description = "Short explanation of the reasoning"
    )

class GuardRailResult(Explanation):
    """
    Guard rail check of a user chat message to decide whether to pass it through.
    Contains a result code and explanation text.
    """
    result: CheckResult = Field(
        description = "Whether the message is safe to accept"
    )