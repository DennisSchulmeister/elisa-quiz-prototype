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

class Stateless(BaseModel):
    """
    Sentinel state model for stateless agents.
    """

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
