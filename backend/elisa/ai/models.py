# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations
from pydantic   import BaseModel, Field
from typing     import Any, Literal
from uuid       import uuid4

class SystemMessageContent(BaseModel):
    """
    System message with an error or warning.
    """
    type:     Literal["system"] | str = "system"
    severity: Literal["info", "warning", "error", "critical"]
    text:     str = ""
    
    def ready_to_stream(self):
        """
        Only start streaming if the type is complete and there is already some text.
        """
        return self.type == "system" and self.text

class SpeakMessageContent(BaseModel):
    """
    Spoken message content for a plain and simple chat message.
    """
    type:  Literal["speak"] | str = "speak"
    speak: str = ""

    def ready_to_stream(self):
        """
        Only start streaming if the type is complete and there is already some text.
        """
        return self.type == "speak" and self.speak

class ThinkMessageContent(BaseModel):
    """
    A single thought or reasoning step.
    """
    type:  Literal["think"] | str = "think"
    think: str = ""

    def ready_to_stream(self):
        """
        Only start streaming if the type is complete and there is already some text.
        """
        return self.type == "think" and self.think
    
class ProcessStep(BaseModel):
    """
    A single process step in a sequential background process.
    """
    name:   str = ""
    status: Literal["planned", "running", "finished", "aborted"] | str = "planned"

class ProcessMessageContent(BaseModel):
    """
    Progress of a sequential background process.
    """
    type:  Literal["process"] | str = "process"
    steps: list[ProcessStep] = []

    def ready_to_stream(self):
        """
        Only start streaming if the type is complete
        """
        return self.type == "process"
    
class ActivityMessageContent(BaseModel):
    """
    An interactive activity with custom content and custom UI, e.g. a quiz game.
    The actual activity is managed globally with the message referencing it in
    the chat history.
    """
    type:     Literal["activity"] | str = "activity"
    agent:    AgentCode
    activity: ActivityCode
    id:       ActivityId
    title:    str

    def ready_to_stream(self):
        """
        Only start streaming if the type is complete and there is already some text.
        """
        return self.type == "activity" and self.title
        
class UserChatMessage(BaseModel):
    """
    A single chat message sent from the user to the assistant.
    """
    id:        str = Field(default_factory = lambda: str(uuid4()))
    source:    Literal["user"] = "user"
    transient: bool = False
    content:   SpeakMessageContent

AssistantChatMessageContent = SystemMessageContent | SpeakMessageContent | ThinkMessageContent | ProcessMessageContent | ActivityMessageContent
"""Allowed content types for assistant chat messages"""

class AssistantChatMessage(BaseModel):
    """
    A single chat message as sent from the assistant to the user.
    """
    id:        str = Field(default_factory = lambda: str(uuid4()))
    source:    Literal["assistant"] = "assistant"
    transient: bool = False
    agent:     AgentCode = ""
    content:   AssistantChatMessageContent | None = None
    finished:  bool = True

ChatMessage = UserChatMessage | AssistantChatMessage
"""User or assistant chat message"""

class ConversationMemory(BaseModel):
    """
    Short-term conversational memory that provides context to the LLM about the
    previously exchanged chat messages. Its purpose is to make the LLM "remember"
    what was said before.
    
    The strategy is to keep the past N messages verbatim and to accumulate all older
    messages in a fading summary. This bounds the context window for the LLM and simulates
    human memory, which cannot remember details for long, either.
    """
    messages: list[ChatMessage] = []
    previous: str = ""

class MemoryUpdate(BaseModel):
    """
    An update to the conversational memory that appends new messages and updates
    the fading summary. The other fields allow the client to keep its local memory
    in sync with the server, if the chat is saved on the client.
    """
    chat_title:   str = ""
    new_messages: list[ChatMessage]
    keep_count:   int
    previous:     str

class MessageHistory(BaseModel):
    """
    Message history that records all chat messages in sequential order.
    """
    messages: list[ChatMessage] = []

class PersistedState(BaseModel):
    """
    Client-persisted state of a chat.
    """
    title:      str
    memory:     ConversationMemory
    agents:     AgentStates
    activities: ActivityStates

PersistenceStrategy = Literal["none", "client", "server", "both"]
"""Persistence strategy where a chat is saved"""

class ChatKey(BaseModel):
    """
    Key-fields for persisted chats.
    """
    username:  str
    thread_id: str

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

AgentCode = str
"""Unique short-code to distinguish agent types"""

AgentStates = dict[AgentCode, dict]
"""Persistent state of all agents"""

ActivityCode = str
"""Unique short-code to distinguish activity types"""

ActivityId = str
"""Globally unique activity id (GUID string)"""

ActivityStatus = Literal["created", "running", "paused", "finished"]
"""Current status of an activity """

class ActivityState(BaseModel):
    """
    Shared state of an interactive activity.
    """
    id:       ActivityId = Field(default_factory = lambda: str(uuid4()))
    agent:    AgentCode
    activity: ActivityCode
    title:    str
    status:   ActivityStatus
    data:     dict

ActivityStates = dict[ActivityId, ActivityState]
"""Persistent state of all activities"""

class StateUpdate(BaseModel):
    """
    A single object mutation. The path used dot-notation, e.g.
    "question.answers[0]"` or `"text".
    """
    path:  str
    value: Any

class AgentUpdate(StateUpdate):
    """
    Mutation to an agent's state.
    """
    agent: AgentCode

class ActivityUpdate(StateUpdate):
    """
    Mutation to an activity's state.
    """
    id: ActivityId