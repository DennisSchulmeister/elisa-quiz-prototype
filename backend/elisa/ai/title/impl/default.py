# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations
from typing     import override
from typing     import TYPE_CHECKING

from ...shared  import default_summary_message
from ..base     import TitleGeneratorBase

if TYPE_CHECKING:
    from ..types import ChatTitle

class DefaultTitleGenerator(TitleGeneratorBase):
    """
    Default title generator implementation. Uses the default LLM chat completion client
    to suggest a title for new conversations, but only if the user has already shared
    a learning interest.
    """

    @override
    async def suggest_title(self) -> "ChatTitle":
        """
        Suggest conversation title.
        """
        role_description = """
            You are a professional title editor.

            Role: Meeting participant tasked with titling the conversation.  
            
            Goal: Distill the core of the previous conversation into a short,
            descriptive, and memorable title.  
            
            Backstory: With a background in editorial work and content curation,
            you excel at capturing the essence of discussions in just a few words.  
            
            Tone: Clear, concise, and informative – like a headline that quickly
            tells readers what the conversation was about.
        """

        user_message = """
            Task: Write a title for the conversation.

            Expected Output: A short yet informative headline.

            Constraint: Only provide a title, if I have at least stated my learning interest.

            Language: Please respond in <language_code>{{ language }}</language_code>.
        """

        return await self._assistant.client.chat.completions.create(
            messages = [
                {"role": "system", "content": role_description},
                {"role": "system", "content": default_summary_message},
                {"role": "user",   "content": user_message},
            ],
            context = {
                "memory":   self._assistant.state.memory,
                "language": self._assistant.language,
            },
            response_model = ChatTitle,
        )