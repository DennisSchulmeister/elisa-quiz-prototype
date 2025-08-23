# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from typing             import override
from typing             import TYPE_CHECKING

from ...shared.messages import default_summary_message
from ..base             import AgentRouterBase
from ..types            import ChooseAgentResult

if TYPE_CHECKING:
    from ...types import UserChatMessage

class DefaultAgentRouter(AgentRouterBase):
    """
    Default agent router implementation. Uses the default LLM chat completion client
    to select the agent to handle each incoming user message.
    """

    @override
    async def choose_agent(self, msg: "UserChatMessage") -> "ChooseAgentResult":
        """
        Inspect message summary, which already contains the current user message, and
        decide which agent should handle it.
        """
        return await self._assistant.client.chat.completions.create(
            messages = [
                {
                    "role": "system",
                    "content": """
                        You are an expert agent router.

                        Role: Triage agent responsible for routing user messages for optimum results.

                        Goal: Decide which agent is best suited to handle the incoming message.  
                    """,
                }, {
                    "role": "system",
                    "content": default_summary_message,
                }, {
                    "role": "system",
                    "content": """
                        Task: Review the user's message and select the most appropriate agent from the
                        provided list, based on each agent's description and supported learning activities.
                        
                        Instructions:
                        
                        {% if current_agent %}
                        * Consider both the current message and recent conversation context to make an
                            informed decision. If unsure, prefer the currently active agent.
                        {% else %}
                        * Consider both the current message and recent conversation context to make an
                            informed decision.
                        {% endif %}

                        {% if current_activity %}
                        * If multiple agents are suitable and the message suggests interest in choosing
                            a different activity, ask the user to choose between the relevant options.
                        {% else %}
                        * If multiple agents are suitable, ask the user to choose between the relevant options.
                        {% endif %}

                        * If no clear match is found, choose the fallback agent named "{{ default_agent }}".

                        Available Agents: {{ all_agents }}

                        {% if current_agent %}
                        Current Agent:
                        
                        {{ current_agent }}
                        {% endif %}

                        {% if current_activity %}
                        Current Activity:
                        
                        {{ current_activity }}
                        {% endif %}

                        Language: Please respond in <language_code>{{ language }}</language_code>.
                    """,
                }, {
                    "role": "user",
                    "content": msg.content.speak,
                }
            ],
            context = {
                "default_agent":    self._get_default_agent_code(),
                "current_agent":    self._get_current_agent_message(),
                "current_activity": self._get_current_activity_message(),
                "all_agents":       self._get_all_agents_message(),
                "language":         self._assistant.language,
                "memory":           self._assistant.state.memory,
            },
            response_model = ChooseAgentResult,
        )