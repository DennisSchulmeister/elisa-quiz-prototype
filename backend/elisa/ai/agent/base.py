# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from typing   import TYPE_CHECKING
from pydantic import BaseModel

from .types   import ActivityUpdate
from .types   import AgentUpdate
from .types   import Stateless

if TYPE_CHECKING:
    from typing       import Type

    from ...auth.user import User
    from ..chat       import ChatManager
    from ..types      import AgentCode
    from ..types      import UserChatMessage
    from .types       import ProcessChatMessageResult

class AgentBase:
    """
    Base class for AI agents managed by the chat manager.
    """

    #=========================================
    # Class attributes for agent configuration
    #=========================================

    code: "AgentCode"
    """Unique short-code to distinguish agent types"""

    personas: "dict[str, Type[PersonaBase]]" = {}
    """Personas used by this agent"""

    activities: dict[str, str] = {}
    """Activity codes and short descriptions"""

    state: Type[BaseModel] = Stateless
    """Persistent agent state (must be default-constructable)"""

    def __init__(self, manager: "ChatManager"):
        """
        Constructor. Save reference to top-level chat manager and initialize the contained
        persona instances and state model.
        """
        self._manager  = manager
        self._personas = {code: self.personas[code](self, manager) for code in self.personas.keys()}
        self._state    = self.state()

        self.initialize_default_state()

    #==================================
    # Hooks to customize agent behavior
    #==================================

    def initialize_default_state(self):
        """
        Override this method to populate `self._state` with the default state, if your agent
        maintains state and you need finer control than possible with the default values of
        the model class
        
        Note:
            This is called in `__init__()` so that the agent instance might not yet be fully
            initialized. You can directly assign values to the properties of `self._state`
            but should avoid replacing the whole object.
        """
        pass

    async def process_chat_message(self, msg: UserChatMessage, user: User) -> ProcessChatMessageResult:
        """
        Respond to the given user message. By default, this delegates to a persona
        determined by `determine_persona()`, but you can override either method for
        complete control.

        Parameters:
            msg:  The chat message to respond to.
            user: User authentication context.
        
        Returns:
            True if the message was handled by this agent (an agent response will be sent).
            False or an agent code if the message should be handed over to another agent.
            See `ProcessChatMessageResult` documentation for details.

        Note:
            Usually, no response should be sent to the client if the agent cannot handle
            the message. Returning True means an agent response will be sent, but the
            response may still instruct the manager to hand over to another agent, meaning
            the LLM ultimately decides if the message was handled.
        
        To handle the message create a response, call the manager's `_send_agent_response()`
        or `_stream_agent_response()` methods and return True.
        """
        persona_code = await self.determine_persona(msg, user)

        if persona_code:
            return await self._personas[persona_code].process_chat_message(msg, user)
    
        return False

    async def determine_persona(self, msg: UserChatMessage, user: User) -> str | None:
        """
        Determines which persona should respond to the given user message. Called by the default
        implementation of `process_chat_message()` to select the most appropriate persona based on
        the agent's state. If the agent has only one persona, it is returned automatically.

        If the message should be handled by another agent altogether, return an empty string or `None`.

        To customize agent behavior, override this method to implement custom persona selection logic,
        or override `process_chat_message()` for complete control.
        """
        persona_codes = list(self.personas.keys())

        if len(persona_codes) == 1:
            return persona_codes[0]

    #===============================================
    # Utility methods called by implementing classes
    #===============================================

    async def update_agent(self, path: str, value):
        """
        Update the agent's persistent state. Use this instead of directly mutating `self._state`,
        so that the change can be properly persisted without sending the whole state over the wire
        after each chat message exchange. Direct changes to `self._state` will not be persisted!

        Parameters:
            path: Property to change (with dot and array notation, e.g. `"questions.answers[0]"`)
            value: New value or None to delete the value
        
        Note:
            * Deleting an array index removes the element from the array (e.g. `"menu.choices[1]"`).
              All other values will simply be overwritten with `None` with the key remaining set.
            
            * `KeyError` is raised, when the path cannot be fully resolved.
        """
        _apply_update(self._state, path, value)

        await self._manager.propagate_agent_update(
            update = AgentUpdate(
                agent = self.code,
                path  = path,
                value = value,
            ),
        )
    
    async def update_activity(self, path: str, value):
        """
        Update the current activity's shared state, similar to how the agent's state is updated.
        Again, use this instead of directly modifying the activity state to make sure that the
        change is propagated to the client and persisted properly.

        Parameters:
            path: Property to change (with dot and array notation, e.g. `"questions.answers[0]"`)
            value: New value or None to delete the value
        
        Notes:
            * Deleting an array index removes the element from the array (e.g. `"menu.choices[1]"`).
              All other values will simply be overwritten with `None` with the key remaining set.
            
            * `KeyError` is raised, when the path cannot be fully resolved.

            * `TypeError` is raised when there is no current activity or the activity belongs to
              another agent.
            
            * The activity title and status can be changed via the paths `"title"` and `"status"`,
              as defined in `ActivityState`.
        """
        if not self._manager._current_activity:
            raise TypeError("No current activity found")
        
        if self._manager._current_activity.agent != self.code:
            raise TypeError(f"Agent {self.code} cannot update activities by agent {self._manager._current_activity.agent}")
    
        _apply_update(self._manager._current_activity, path, value)

        await self._manager.propagate_activity_update(
            ActivityUpdate(
                id    = self._manager._current_activity.id,
                path  = path,
                value = value,
                origin = "agent",
            ),
        )

class PersonaBase:
    """
    Personas enable an agent to exhibit distinct behaviors in different states.
    In agents with multiple personas, each persona handles its own LLM calls,
    allowing for unique system prompts and parameters, while all personas share
    the agent's state.
    """
    def __init__(self, agent: AgentBase, manager: "ChatManager"):
        """
        Constructor. Save reference to the parent agent.
        """
        self._agent   = agent
        self._manager = manager

    async def process_chat_message(self, msg: UserChatMessage, user: User) -> ProcessChatMessageResult:
        """
        Respond to the given user message.

        To handle the message create a response, call the manager's `_send_agent_response()`
        or `_stream_agent_response()` methods and return True. Otherwise return False or an
        agent code to hand-over to another agent.
        """
        return False

def _apply_update(obj, path: str, value = None):
    """
    Internal implementation for the `update_state()` and `update_activity()` methods
    that actually performs the requested update. Raises `KeyError` when the path
    cannot be fully resolved.
    """
    parent   = None
    child    = obj
    key      = 0
    is_index = False

    for subpath in path.split("."):
        # Traverse child properties
        parent = child
        key    = subpath.split("[")[0]

        if hasattr(child, key):
            child = getattr(child, key)
        elif key in child:
            child = child[key]
        else:
            parent = None
            break
    
        # Traverse list indices
        if "[" in subpath and "]" in subpath:
            for index in subpath.split("[")[1:]:
                parent = child
                key = int(index.replace("]", ""))
                child = child[key]

    if not parent:
        raise KeyError(f"Key not found: {path}")
    
    if not value and is_index:
        del parent[key]
    else:
        parent[key] = value