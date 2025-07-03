# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from pydantic import BaseModel

class StartChatMessage(BaseModel):
    """
    X
    """

# class StartConversationMessage(WebsocketMessage):
#     """
#     Start new conversation and trigger welcome message by LLM.
#     """
#     language: str
# 
# class ResumeConversationMessage(WebsocketMessage, PersistedConversation):
#     """
#     Persisted conversation to resume from a previous session.
#     """
# 
# class ChatInputMessage(WebsocketMessage):
#     """
#     Chat input from the user.
#     """
#     text: str
#     language: str
# 
# class UpdateActivityMessage(WebsocketMessage, UpdateActivityData):
#     """
#     Message to exchange the updated internal state of a currently running
#     interactive activity between client and server.
#     """