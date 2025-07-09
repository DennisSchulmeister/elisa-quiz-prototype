# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from pydantic          import BaseModel
from ...ai.agent.types import ActivityId
from ...ai.types       import PersistedState
from ...ai.types       import PersistenceStrategy

class StartChat(BaseModel):
    """
    Message sent by the client to start a new chat or resume a previous chat.
    Depending on where the chat is saved, the client only sends the thread id
    or the full chat state to resume a chat.
    """
    username:    str = ""
    thread_id:   str = ""
    persistence: PersistenceStrategy = "none"
    state:       PersistedState | None = None

class ChangeLanguage(BaseModel):
    """
    Message sent by the client, after the user interface language has been changed,
    so that the AI agent from then on responds in the same language.
    """
    language: str

class StartActivity(BaseModel):
    """
    Message sent by the client to start or resume an interactive activity.
    """
    id: ActivityId