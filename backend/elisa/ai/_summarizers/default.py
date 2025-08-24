# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__    import annotations
from typing        import override
from .._summarizer import SummarizerBase, MessageSummary

class DefaultSummarizer(SummarizerBase):
    """
    Default title generator implementation. Uses the default LLM chat completion client
    to suggest a title for new conversations, but only if the user has already shared
    a learning interest.    
    """

    @override
    async def compress_memory(self):
        """
        Compress conversation memory.
        """
        summary_messages = self._assistant.state.memory.messages[:-self.keep_count]
        self._assistant.state.memory.messages = self._assistant.state.memory.messages[-self.keep_count:]

        if summary_messages:
            role_description = """
                You are an experienced minute-taker.

                Role: Active meeting participant responsible for writing concise and
                accurate minutes.  

                Goal: Summarize the previous conversation compactly without losing essential
                information or nuance.  

                Backstory: As a professional writer with extensive experience in documenting
                interviews and dialogues, you know how to distill conversations into clear,
                structured summaries that remain faithful to the original.  

                Tone: Neutral, precise, and focused – like a diligent observer capturing what
                matters most.
            """

            user_message = """
                Task: Update the meeting minutes and summarize the previous conversation.

                Expected Output: A clear summary of all previous contributions, compact yet
                faithful to the original.

                Previous summary:
                
                <summary>
                    {{ previous }}
                </summary>

                What was said since then:
                
                <messages>
                    {% for message in messages %}
                    <message source="{{ message.source }}">
                        {{ message.content}}
                    </message>
                    {% endfor %}
                </messages>

                Language: Please respond in <language_code>{{ language }}</language_code>.
            """
            response = await self._assistant.client.chat.completions.create(
                messages = [
                    {"role": "system", "content": role_description},
                    {"role": "user",   "content": user_message},
                ],
                context = {
                    "previous": self._assistant.state.memory.previous,
                    "messages": summary_messages,
                    "language": self._assistant.language,
                },
                response_model = MessageSummary,
            )

            self._assistant.state.memory.previous = response.summary