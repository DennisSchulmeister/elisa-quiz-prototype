# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations
from pydantic   import BaseModel

class PrivacySettingsMessage(BaseModel):
    """
    Privacy settings with the different types of user consent e.g. to track
    application usage time or learning topics.
    """
    record_usage_time:      bool = False
    record_learning_topics: bool = False