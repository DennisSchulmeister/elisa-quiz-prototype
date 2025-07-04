# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from abc             import ABC
from abc             import abstractmethod
from instructor      import AsyncInstructor
from typing          import AsyncGenerator
from typing          import Protocol

from .activity.types import ActivityTransaction
from .types          import AgentChatMessage
from .types          import AgentChatMessageContent
from .types          import MemoryTransaction

class ChatAgentCallback(ABC):
    """
    Mixin class that defines several callback functions to be called by the chat
    agent in order to send messages back to the client. Must be implemented by
    the websocket handler class owning the chat agent.
    """
    @abstractmethod
    async def send_agent_chat_message(self, msg: AgentChatMessage):
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
    async def send_activity_transaction(self, tx: ActivityTransaction):
        """
        Send activity update to the client after modification by the agent.
        """

class FilterAgentChatMessageContent(Protocol):
    """
    Callback function to modify partial message contents before they are streamed
    out to the client.
    """
    async def __call__(self, msg: AgentChatMessageContent) -> AgentChatMessageContent:
        ...

class ChatAgentInternal(ABC):
    """
    Mixin class that defines internal callback functions for down-stream objects
    in the main chat agent. These methods provide the means to access the global
    LLM client object, websocket callback and to send or stream agent messages.
    """
    @abstractmethod
    def _get_client(self) -> AsyncInstructor:
        """
        Provide LLM client to down-stream objects.
        """
    
    @abstractmethod
    def _get_callback(self) -> ChatAgentCallback:
        """
        Provide the websocket callback to down-stream objects.
        """

    @abstractmethod
    async def _stream_agent_message(
        self,
        partials:  AsyncGenerator,
        filter_cb: FilterAgentChatMessageContent|None = None
    ):
        """
        Internal method called by the agent and various activities to stream out an
        LLM-generated agent chat message to the client and to append the message to
        the memory. This is the default way to send messages to the client.

        Parameters:
            partials: Return value of `self.client.chat.completions.create_partial()`
            filter:   Callback function to modify the LLM-generated message content
        """
    
    @abstractmethod
    async def _send_agent_message(self, content: AgentChatMessageContent):
        """
        Internal method called by the agent and various activities to send out an
        LLM-generated agent chat message (all at once without streaming) to the
        client and append it to the memory. This is meant for small messages where
        streaming doesn't improve the UX.
        """