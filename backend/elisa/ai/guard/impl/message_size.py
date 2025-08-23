# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import os

from typing   import override
from typing   import TYPE_CHECKING

from ..base   import GuardRailBase
from ..types  import Explanation
from ..types  import GuardRailResult

if TYPE_CHECKING:
    from ...types import UserChatMessage

class MessageSizeGuardRail(GuardRailBase):
    """
    Guard rail implementation that checks the maximal allowed message size.
    Large messages are rejected to favor more conversation like usage.
    """

    max_message_size = -1
    """Maximum allowed characters for user chat messages"""

    @override
    @classmethod
    def read_config(cls):
        """
        Read configuration values during server start-up.
        """
        max_message_size = os.environ.get("ELISA_MAX_MSG_SIZE", "25000")

        try:
            cls.max_message_size = int(max_message_size)
        except ValueError:
            raise ValueError(f"ELISA_MAX_MSG_SIZE - Must be integer: {max_message_size}")
        
    @override
    async def check_message(self, msg: "UserChatMessage") -> GuardRailResult:
        """
        Inspect the given user message and decide whether it goes through or is rejected.
        """
        check_result = GuardRailResult(result="accept", text="")

        if len(msg.content.speak) > self.max_message_size:
            explanation = await self._assistant.client.chat.completions.create(
                messages = [
                    {
                        "role": "user",
                        "content": """
                            Role: You are a vigilant content safety reviewer.

                            Task: Please explain in a short and friendly way that my last message exceeds the
                            maximum allowed size. Include, that you are designed for interactive usage – relying
                            on verbal conversation and interactive activities to aid my learning rather then just
                            processing copy&pasted notes.

                            Language: Please respond in <language_code>{{ language }}</language_code>.
                        """,
                    }
                ],
                context = {
                    "language": self._assistant.language,
                },
                response_model = Explanation,
            )

            check_result.result = "reject-warning"
            check_result.text   = explanation.text

        return check_result
