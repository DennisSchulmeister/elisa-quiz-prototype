# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

class ChatAgent:
    """
    Top-level instance of the AI chat agent. Receives chat messages from the
    user, streams chat messages back to the user and applies global guard rails
    like rejecting profanity or harassments.
    """