# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from pydantic import BaseModel

class DefaultState(BaseModel):
    """
    Internal state of the default agent. Simply tracks whether the initial
    greetings have been exchanged or we still need to say hello to the user.
    """
    welcome_done: bool = False