# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from pydantic import BaseModel
from typing   import Any
from typing   import Literal

AgentCode = str
"""Unique short-code to distinguish agent types"""

AgentStates = dict[AgentCode, BaseModel]
"""Persistent state of all agents"""

ActivityCode = str
"""Unique short-code to distinguish activity types"""

ActivityId = str
"""Globally unique activity id (GUID string)"""

ActivityStatus = Literal["created", "running", "paused", "finished", "aborted"]
"""Current status of an activity """

ActivityStates = dict[ActivityId, BaseModel]
"""Persistent state of all activities"""

class Stateless(BaseModel):
    """
    Sentinel state model for stateless agents.
    """

class ActivityState(BaseModel):
    """
    Shared state of an interactive activity.
    """
    agent: AgentCode
    """Agent responsible for running the activity"""

    activity: ActivityCode
    """Activity type"""

    id: ActivityId
    """Globally unique activity id"""

    title: str
    """Activity title"""

    status: ActivityStatus
    """Whether the activity is currently running or not"""

    data: BaseModel
    """Shared data of the activity (depending on the activity type)"""

class StateUpdate(BaseModel):
    """
    A single object mutation.
    """
    path: str
    """Affected path, e.g.: `"question.answers[0]"` or `"text"`"""

    value: Any
    """New value"""

class AgentUpdate(StateUpdate):
    """
    Mutation to an agent's state.
    """
    agent: AgentCode
    """Agent code"""

class ActivityUpdate(StateUpdate):
    """
    Mutation to an activity's state.
    """
    id: ActivityId
    """Activity instance id"""

    origin: Literal["agent", "user"]
    """Which side mutated the state"""

ProcessChatMessageResult = bool | AgentCode
"""
Result of processing a chat message by an agent or one of its personas.
This return value determines how the chat manager proceeds:

 - Boolean `true`: The message has successfully handled. The manager doesn't
   need to do anything.

 - Boolean `false`: The message could not be handled and should probably be
   transferred to another agent. The manager will use the LLM to try and find
   another agent.

 - String: The message should be handed over to the agent with the given code.
"""

# class AgentResponse(BaseModel):
#     """
#     Thin wrapper around an agent chat message to allow the agent to hand-over
#     to another agent.
#     """
#     handover: str | None = None
#     """Code of the next agent to hand-over to or "*" if unknown"""
# 
#     message: AgentChatMessage | None = None
#     """Chat message from the agent to the user"""
