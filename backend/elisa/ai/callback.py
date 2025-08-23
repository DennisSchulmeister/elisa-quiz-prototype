# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations

from abc          import ABC
from abc          import abstractmethod

from .agent.types import ActivityUpdate
from .agent.types import AgentUpdate
from .types       import AssistantChatMessage
from .types       import MemoryUpdate

class ChatAgentCallback(ABC):
    """
    Mixin class that defines several callback functions to be called by the chat
    agent in order to send messages back to the client. Must be implemented by
    the websocket handler class owning the chat agent.
    """
    @abstractmethod
    async def send_assistant_chat_message(self, msg: AssistantChatMessage):
        """
        Send an assistant chat message to the client.
        """
    
    @abstractmethod
    async def send_memory_update(self, update: MemoryUpdate):
        """
        Send conversation memory update to the client, so that it can save the
        updated memory in the persistent chat history. This message is only sent,
        when the chat is saved on the client.
        """
    
    @abstractmethod
    async def send_agent_update(self, update: AgentUpdate):
        """
        Send agent state update to the client, so that it can save the updated
        agent state in the persistent chat history. This message is only sent, when
        the chat is saved on the client.
        """

    @abstractmethod
    async def send_activity_update(self, update: ActivityUpdate):
        """
        Send activity state update to the client, so that it can update the UI
        accordingly and save the updated activity state in the persistent chat
        history, if the chat is saved on the client.
        """
