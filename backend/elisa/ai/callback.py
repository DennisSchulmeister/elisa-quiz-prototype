# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from abc             import ABC
from abc             import abstractmethod

from .activity.types import ActivityTransaction
from .types          import AgentChatMessage
from .types          import MemoryTransaction

class ChatAgentCallbackABC(ABC):
    """
    Mixin class that defines several callback functions to be called by the chat
    agent in order to send messages back to the client. Must be implemented by
    the websocket handler class owning the chat agent.
    """
    @abstractmethod
    async def send_agent_chat_message(self, message: AgentChatMessage):
        """
        Send an agent chat message to the client.
        """
    
    @abstractmethod
    async def send_memory_transaction(self, tx: MemoryTransaction):
        """
        Update persisted conversation memory, when it is saved by the client.
        This message is only generated for conversations that are persisted
        by the client (instead of the server or not at all).
        """
    
    @abstractmethod
    async def send_activity_transaction(self, data: ActivityTransaction):
        """
        Update content or state of an activity.
        """
