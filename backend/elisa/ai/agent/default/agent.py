# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations
from typing     import TYPE_CHECKING

from ...shared  import default_role_description, default_summary_message
from ..base     import AgentBase

if TYPE_CHECKING:
    from ....auth.user import User
    from ...types      import AssistantChatMessage, UserChatMessage, SpeakMessageContent
    from ..types       import ProcessChatMessageResult
    from .types        import DefaultState

class DefaultAgent(AgentBase[DefaultState]):
    """
    Default agent that responds to all chat messages not targeted at a more specialized agent.
    """
    code = "default-agent"

    def __init__(self, **kwargs):
        super().__init__(state=DefaultState(), **kwargs)

    async def greet_user(self):
        """
        Say hello to the user to initiate the conversation, if not already done.
        The "if not done" is important so that the greeting is not repeated when
        the user resumes an old chat.
        """
        if self._state.welcome_done:
            return

        await self._assistant.stream_assistant_chat_message(
            assistant_message = AssistantChatMessage(),
            partials          = self._assistant.client.chat.completions.create_partial(
                messages = [
                    {
                        "role": "system", 
                        "content": default_role_description,
                    }, {
                        "role": "user", 
                        "content": """
                            Task: Give me a warm welcome and introduce yourself.
                            Then ask for my name and what topic I want to learn.

                            Language: Please respond in <language_code>{{ language }}</language_code>.
                        """,
                    }
                ],
                context = {
                    "language": self._assistant.language,
                },
                response_model = SpeakMessageContent,
            ),
        )

        await self.update_agent("welcome_done", True)
    
    async def process_chat_message(self, msg: UserChatMessage, user: User) -> ProcessChatMessageResult:
        """
        Respond to the given user chat message.
        """
        await self._assistant.stream_assistant_chat_message(
            user_message      = msg,
            assistant_message = AssistantChatMessage(),
            partials          = self._assistant.client.chat.completions.create_partial(
                messages = [
                    {
                        "role": "system", 
                        "content": default_role_description,
                    }, {
                        "role": "system", 
                        "content": default_summary_message,
                    }, {
                        "role": "system", 
                        "content": """
                            Task: Answer the user message below. Always try to be supportive and suggest
                            possible follow-ups to increase the learning effect.

                            Language: Please respond in <language_code>{{ language }}</language_code>.
                        """,
                    }, {
                        "role": "user",
                        "content": msg.content.speak,
                    }
                ],
                context = {
                    "memory":   self._assistant.state.memory,
                    "language": self._assistant.language,
                },
                response_model = SpeakMessageContent,
            ),
        )

        return True