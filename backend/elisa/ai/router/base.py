# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations
from abc        import ABC, abstractmethod
from typing     import TYPE_CHECKING

from ...shared  import ReadConfigMixin

if TYPE_CHECKING:
    from ..assistant import AIAssistant
    from ..types     import UserChatMessage
    from .types      import ChooseAgentResult

class AgentRouterBase(ABC, ReadConfigMixin):
    """
    Base class for agent router implementations. The agent router (there can only be
    one per conversation) decides which agent should handle an incoming user message
    based on the message itself and typically the last used agent and current activity.
    """

    def __init__(self, assistant: AIAssistant):
        """
        Constructor. Saves a reference to the top-level AI assistant, from which
        also the default LLM chat completion client can be accessed.
        """
        self._assistant = assistant
    
    @abstractmethod
    async def choose_agent(self, msg: UserChatMessage) -> ChooseAgentResult:
        """
        Inspect the given user message and decide which agent should handle it.
        """
    
    def _get_current_agent_message(self) -> str:
        """
        Create a message snippet containing the last used agent, if any. Returns an empty
        string, if not agent has been used before.
        """
        if self._assistant.current_agent:
            return f"""
                <agent>
                    <agent_code>{self._assistant.current_agent.code}<agent_code>
                    <description>{self._assistant.current_agent.__doc__}</description>
                </agent>
            """
        else:
            return ""

    def _get_current_activity_message(self) -> str:
        """
        Create a message snippet containing the current activity, if any. Returns an empty
        string, if no activity is currently running.
        """
        if self._assistant.current_activity:
            _agent = self._assistant.agents[self._assistant.current_activity.agent]
            _description = _agent.activities[self._assistant.current_activity.activity] if _agent else ""

            return f"""
                <activity>
                    <agent_code>{self._assistant.current_activity.agent}</agent_code>
                    <activity_code>{self._assistant.current_activity.activity}</activity_code>
                    <title>{self._assistant.current_activity.title}</title>
                    <description>{_description}</description>
                </activity>
            """
        else:
            return ""
    
    def _get_all_agents_message(self) -> str:
        """
        Create a message snipped containing a list of all available agents along with
        their doc strings as descriptions. Use this instead of directly accessing the
        `AgentRegistry` class to avoid circular imports.
        """
        from ..agent.registry import AgentRegistry
        return AgentRegistry.get_all_agents_message()

    def _get_default_agent_code(self) -> str:
        """
        Return code of the default agent. Use this instead of directly accessing the
        `AgentRegistry` class to avoid circular imports.
        """
        from ..agent.registry import AgentRegistry
        return AgentRegistry.default_agent_code