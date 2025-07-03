# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from .callback import ChatAgentCallback

class ChatAgent:
    """
    Top-level instance of the AI chat agent. Receives chat messages from the
    user, streams chat messages back to the user and applies global guard rails
    like rejecting profanity or harassments.
    """

    def __init__(self, callback: ChatAgentCallback):
        """
        Parameters:
            callback: Websocket handler with callbacks to send messages to the client
        """
        self._callback = callback
        self._record_learning_topic = False

    def set_record_learning_topic(self, allow: bool):
        """
        Update flag whether the user allows to track the learning topics.
        """
        self._record_learning_topic = allow