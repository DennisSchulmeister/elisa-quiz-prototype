# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from typing       import Callable
from typing       import Generic
from typing       import Type
from typing       import TypeVar

from ...auth.user import User
from ..assistant  import AIAssistant
from ..types      import AgentCode
from ..types      import UserChatMessage
from .types       import ActivityUpdate
from .types       import AgentUpdate
from .types       import ProcessChatMessageResult

State = TypeVar("State")
Agent = TypeVar("Agent")

class AgentBase(Generic[State]):
    """
    Base class for the AI agents that implement the the domain logic exhibited
    by the AI assistant.
    """

    #=========================================
    # Class attributes for agent configuration
    #=========================================

    code: "AgentCode"
    """Unique short-code to distinguish agent types"""

    personas: "dict[str, Callable[..., Type[PersonaBase]]]" = {}
    """Personas used by this agent"""

    activities: dict[str, str] = {}
    """Activity codes and short descriptions"""

    def __init__(self, assistant: AIAssistant, state: State):
        """
        Constructor. Save reference to top-level chat manager and initialize the contained
        persona instances and state model.
        """
        self._assistant = assistant
        self._personas  = {}
        self._state     = state

        for code, persona in self.personas.items():
            self._personas[code] = persona()(self, assistant)

    #==================================
    # Hooks to customize agent behavior
    #==================================

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

        Note:
            Usually, no response should be sent to the client if the agent cannot handle the
            message. Returning True means an agent response will be sent, but the response may
            still instruct the assistant to hand over to another agent, meaning the LLM ultimately
            decides if the message was handled.
        
        To handle the message create a response, call the assistant's `_send_assistant_chat_message()`
        or `_stream_assistant_chat_message()` methods and return True. Don't forget to include the user
        message in these calls! Return False or an agent code to hand-over to another agent.

        To start a new activity, first create the activity by calling `create_activity()` on the assistant
        and then sending a chat message with content type "activity" to the client.
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
        after each chat message exchange. Direct changes to `self._state` will not be propagated!

        Parameters:
            path: Property to change (with dot and array notation, e.g. `"questions.answers[0]"`)
            value: New value or None to delete the value
        
        Note:
            * Deleting an array index removes the element from the array (e.g. `"menu.choices[1]"`).
              All other values will simply be overwritten with `None` with the key remaining set.
            
            * `KeyError` is raised, when the path cannot be fully resolved.
        """
        await self._assistant.propagate_agent_update(
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
        if not self._assistant._current_activity:
            raise TypeError("No current activity found")
        
        if self._assistant._current_activity.agent != self.code:
            raise TypeError(f"Agent {self.code} cannot update activities by agent {self._assistant._current_activity.agent}")
    
        await self._assistant.propagate_activity_update(
            ActivityUpdate(
                id     = self._assistant._current_activity.id,
                path   = path,
                value  = value,
            ),
        )

class PersonaBase(Generic[Agent]):
    """
    Personas enable an agent to exhibit distinct behaviors in different states.
    In agents with multiple personas, each persona handles its own LLM calls,
    allowing for unique system prompts and parameters, while all personas share
    the agent's state.
    """
    def __init__(self, agent: Agent, assistant: AIAssistant):
        """
        Constructor. Save reference to the parent agent.
        """
        self._agent     = agent
        self._assistant = assistant

    async def process_chat_message(self, msg: UserChatMessage, user: User) -> ProcessChatMessageResult:
        """
        Respond to the given user message.

        To handle the message create a response, call the assistant's `_send_assistant_chat_message()`
        or `_stream_assistant_chat_message()` methods and return True. Don't forget to include the user
        message in these calls! Return False or an agent code to hand-over to another agent.

        To start a new activity, first create the activity by calling `create_activity()` on the assistant
        and then sending a chat message with content type "activity" to the client.
        """
        return False

default_role_description = """
    You are ELISA – an interactive learning tutor who supports students in their learning journey.

    Role: Experienced assistant lecturer at schools and universities across diverse subjects. 

    Goal: Teach and support each student individually to help them reach their full potential.

    Backstory: Over the years, you’ve developed a student-centered teaching style. You believe
    every learner can succeed and enjoy the process if met with empathy, encouragement, and the
    right guidance.  

    Tonality: Friendly, engaging, motivational, and consistently positive – like a trusted mentor
    who believes in their students.TODO
"""

default_summary_message = """
    Here is a summary of the conversation so far:
    
    <summary>
        {memory.previous}
    </summary>

    Since then the following was additionally said:
    
    <messages>
        {% for message in memory.messages %}
        <message source="{{ message.source }}">
            {{ message.content}}
        </message>
        {% endfor %}
    </messages>
"""