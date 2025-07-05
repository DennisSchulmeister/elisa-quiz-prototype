# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from pydantic        import BaseModel
from pydantic        import Field
from typing          import Literal
from typing          import List

from .activity.types import ActivityData
from .activity.types import ActivityStatus
from .activity.types import ActivityType

class SystemMessageContent(BaseModel):
    """
    System message with an error or warning.
    """
    type: Literal["system"] | str = "system"
    """Content type (System message)"""

    text: str = ""
    """Message text"""
    
    def ready_to_stream(self):
        """
        Only start streaming if the type is complete and there is already some text-
        """
        return self.type == "system" and self.text

class SpeakMessageContent(BaseModel):
    """
    Spoken message content for a plain and simple chat message.
    """
    type: Literal["speak"] | str = "speak"
    """Content type (Regular speech message)"""

    speak: str = ""
    """Message text"""

    def ready_to_stream(self):
        """
        Only start streaming if the type is complete and there is already some text-
        """
        return self.type == "speak" and self.speak

class ThinkMessageContent(BaseModel):
    """
    A single thought or reasoning step.
    """
    type: Literal["think"] | str = "think"
    """Content type (Thought or reasoning step)"""

    think: str = ""
    """Message text"""

    def ready_to_stream(self):
        """
        Only start streaming if the type is complete and there is already some text-
        """
        return self.type == "think" and self.think
    
class ProcessStep(BaseModel):
    """
    A single process step in a sequential background process.
    """
    name: str = ""
    """Process step name"""

    status: Literal["planned", "running", "finished", "aborted"] | str = "planned"
    """Current status"""

class ProcessMessageContent(BaseModel):
    """
    Progress of a sequential background process.
    """
    type: Literal["process"] | str = "process"
    """Content type (Sequential process progress)"""

    steps: List[ProcessStep] = []
    """Status of each individual step"""

    def ready_to_stream(self):
        """
        Only start streaming if the type is complete
        """
        return self.type == "process"
    
class ActivityMessageContent(BaseModel):
    """
    An interactive activity with custom content and custom UI, e.g. a quiz game.
    """
    id: str = ""
    """Activity id"""

    type: Literal["activity"] | str = "activity"
    """Content type (Interactive activity)"""

    activity: ActivityType
    """Activity type"""

    status: ActivityStatus | str = "created"
    """Whether the activity is running"""

    data: ActivityData
    """Shared data with the content and state of the activity"""

    def ready_to_stream(self):
        """
        Only start streaming if the type is complete and there is already some text-
        """
        return self.type == "activity" and self.data
        
class UserChatMessage(BaseModel):
    """
    A single chat message sent from the user to the agent.
    """
    source: Literal["user"] = "user"
    """Message source (always the user)"""

    content: SpeakMessageContent
    """Message content"""

AgentChatMessageContent = SystemMessageContent | SpeakMessageContent | ThinkMessageContent | ProcessMessageContent | ActivityMessageContent
"""Possible content of a LLM-generated agent chat message"""

class AgentChatMessage(BaseModel):
    """
    A single chat message as sent from the agent to the user.
    """
    source: Literal["agent"] = "agent"
    """Message source (always the agent)"""

    id: str
    """Message id for streaming partial messages"""

    content: AgentChatMessageContent
    """Message content"""

ChatMessage = UserChatMessage | AgentChatMessage
"""User or agent chat message"""

class ShortTermMemory(BaseModel):
    """
    Short-term conversation memory that provides context to the LLM about the
    previously exchanged chat messages.
    
    Even though it is persisted along with the long-term memory, its only purpose
    is to make the LLM "remember" what was said before. That's why only the past
    N messages are kept verbatim and all older messages get accumulated into a
    summary. This bounds the context window for the LLM and simulates the memory
    of must humans, who also only remember the details of the most recent events.
    """
    messages: List[ChatMessage] = []
    """The most recent chat messages"""

    previous: str = ""
    """Fading summary of all older messages"""

class LongTermMemory(BaseModel):
    """
    Long-term conversation memory that persists the full details of a conversation
    thread. Unlike real humans all details are remembered, but only to be able to
    rebuild the UI when picking up an old thread and not to provide conversation
    context to the LLM.
    """
    thread_id: str = ""
    """Thread id to distinguish conversations"""

    messages: List[ChatMessage] = []
    """Full chat message list"""

class MemoryTransaction(BaseModel):
    """
    An update to the long-term and short-term conversation memory sent by the agent
    to the persistence layer to update the persisted memory accordingly.
    """
    thread_id: str
    """Thread id to distinguish conversations"""

    title: str = ""
    """Chat title"""

    new_messages: List[ChatMessage]
    """New messages"""

    short_term_n: int
    """Number of recent messages to keep in the short-term memory"""

    previous: str
    """Updated short-term summary of the older messages"""

class StartChat(BaseModel):
    """
    Start new chat conversation or resume previous conversation based
    on its persisted short-term memory.
    """

    language: str
    """Current user interface language"""

    thread_id: str = ""
    """Thread id of previous chat"""

    short_term: ShortTermMemory | None = None
    """
    Short-term memory of previous chat, when persisted on the client. Ignored,
    when the server persists the chat.
    """

    persist: bool = False
    """
    Persist the chat on the server
    """

class ChatTitle(BaseModel):
    """
    Distilled title of the chat conversation so far.
    """
    meaningful: bool = Field(
        description = "Whether the conversation provides enough information for a meaningful title",
    )

    title: str = Field(
        description = "Clear, concise, and informative title for the conversation",
    )

class GuardRailResult(BaseModel):
    """
    Guard rail check of a received chat message to decide whether to pass it through.
    """
    reject: bool = Field(
        description = "Whether the message should be rejected"
    )

    reasoning: str = Field(
        description = "Reasoning behind the classification"
    )