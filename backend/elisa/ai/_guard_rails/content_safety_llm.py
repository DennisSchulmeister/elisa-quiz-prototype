# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__    import annotations
from typing        import override, TYPE_CHECKING
from .._guard_rail import GuardRailBase
from ..models      import GuardRailResult

if TYPE_CHECKING:
    from ..models import UserChatMessage

class ContentSafetyLLMGuardRail(GuardRailBase):
    """
    Guard rail implementation that uses the LLM chat completion client to detect
    unsafe, abusive or otherwise unwanted content.
    """

    max_message_size = -1
    """Maximum allowed characters for user chat messages"""

    @override
    async def check_message(self, msg: UserChatMessage) -> GuardRailResult:
        """
        Inspect the given user message and decide whether it goes through or is rejected.
        """
        return await self._assistant.client.chat.completions.create(
            messages = [
                {
                    "role": "system",
                    "content": """
                        You are a vigilant content safety reviewer.

                        Role: Silent observer responsible for screening each incoming message
                        before it is handled by the ELISA, the interactive AI learning assistant.

                        Goal: Detect and flag any content that is potentially harsh, insulting,
                        harmful, harassing, illegal, abusive, sexual, threatening or otherwise
                        inappropriate for a safe learning environment.

                        Task: Review the user message. If you decide to reject the message, tend
                        to flag the message as critical and give a short but friendly explanation.
                        If the message is rejected, also say that the message will be recorded and
                        manually reviewed.

                        Language: Please respond in <language_code>{{ language }}</language_code>.
                    """,
                }, {
                    "role": "user",
                    "content": msg.content.speak,
                }
            ],
            context = {
                "message":  msg.content.speak,
                "language": self._assistant.language,
            },
            response_model = GuardRailResult,
        )