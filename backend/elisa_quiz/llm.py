# Elisa: AI Learning Quiz
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import json, os, typing, uuid

from langchain.chat_models       import init_chat_model
from langchain_core.messages     import HumanMessage
from langchain_core.messages     import HumanMessage
from langchain_core.prompts      import ChatPromptTemplate
from langchain_core.prompts      import ChatPromptTemplate
from langchain_core.prompts      import HumanMessagePromptTemplate
from langchain.prompts           import PromptTemplate
from langchain_core.prompts      import SystemMessagePromptTemplate
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph             import START
from langgraph.graph             import StateGraph
from typing_extensions           import TypedDict

class _State(TypedDict):
    """
    Shared state for all nodes in the LLM graph.
    """
    buffer: list
    """Past messages not yet contained in the summary."""

    summary: str
    """Constantly updated summary of the past conversation"""

    user_input: str
    """Currently processed user input message"""

    language: str
    """Currently selected language by the user."""

SendMessageCallback = typing.Callable[[str, dict], typing.Awaitable[None]]
"""Type hint for callback function that sends back chat answers to the client."""

class ChatAgent:
    """
    Wrapper class that simplifies integration with our websocket handler.
    Wraps a few building blocks from LangChain and LangGraph to build a
    very basic chat agent with streaming support.
    """
    def __init__(self):
        # Individual thread id to distinguish concurrent conversations
        self.thread_id = str(uuid.uuid4())

        # Chat model that does all the heavy work
        self.chat_model = init_chat_model(
            model          = os.environ.get("LLM_CHAT_MODEL"),
            model_provider = os.environ.get("LLM_MODEL_PROVIDER"),
        )

        # Nodes are callables that receive the shared state. Edges connect nodes.
        # Nodes return state updates (only what needs to be changed).
        workflow = StateGraph(state_schema=_State)

        workflow.add_edge(START, "send_user_message_to_llm")
        workflow.add_node("send_user_message_to_llm", self._send_user_message_to_llm)

        workflow.add_edge("send_user_message_to_llm", "summarize_past_conversation")
        workflow.add_node("summarize_past_conversation", self._summarize_past_conversation)

        memory = MemorySaver()
        self.app = workflow.compile(checkpointer = memory)
        
    async def _send_user_message_to_llm(self, state: _State):
        """
        LangGraph node that calls the LLM to send the system prompt, the summary of the
        previous conversation and the latest user message to the LLM to generate a reply.
        """
        prompt_template = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(_SYSTEM_PROMPT),
            SystemMessagePromptTemplate.from_template(_SUMMARY_PROMPT if state.get("summary", "") else ""),
            HumanMessagePromptTemplate.from_template(_USER_MESSAGE),
        ])

        prompt = prompt_template.invoke(dict(state))
        response = await self.chat_model.ainvoke(prompt)

        return {
            # Remove user input from state as we handled it now
            "user_input": "",

            # Extend message buffer with question and answer. This will be picked by
            # the next time by the summary node summarize the conversation into a
            # single context message
            #
            # CAVEAT: Don't save message instances here, as they would automatically
            # be streamed to the client.
            "buffer": [
                *state.get("buffer", []),
                {"type": "human", "content": state["user_input"]},
                {"type": "agent", "content": response.content},
            ],
        }
    
    async def _summarize_past_conversation(self, state: _State):
        """
        LangGraph node that first asks the LLM to update the summary of the previous conversation,
        so that when the actual user message is sent to the LLM the summary can be provided as a
        context. We use this strategy because a simple message buffer has shown that the LLM often
        repeats itself by repeating parts of the previous answers with each message.
        """
        if not state.get("buffer", []):
            return {"summary": ""}
        
        template = _EXTEND_SUMMARY_MESSAGE if state.get("summary", "") else _NEW_SUMMARY_MESSAGE
        prompt_template = PromptTemplate(input_variables=["buffer", "summary", "language"], template=template)

        prompt = prompt_template.invoke({
            "buffer":   state.get("buffer"),
            "summary":  state.get("summary"),
            "language": state.get("language"),
        })

        response = self.chat_model.invoke(prompt)
        return {"summary": response.content, "buffer": []}

    async def invoke_with_new_user_message(self, text: str, language: str, callback: SendMessageCallback) -> None:
        """
        Called from the websocket handler to invoke the graph with another user message.
        """
        reply_id    = str(uuid.uuid4())
        reply_text  = ""
        json_blocks = []
        json_found  = False

        def consume_chunk(chunk: str):
            nonlocal json_blocks, json_found, reply_text

            if not json_found:
                reply_text += chunk

                if "```json" in reply_text:
                    json_found = True
                    json_blocks.append("")
                    splitted = reply_text.split("```json", maxsplit=1)

                    if len(splitted) == 1:
                        reply_text = splitted[0]
                    else:
                        reply_text, remaining_chunk = splitted
                        consume_chunk(remaining_chunk)
            else:
                json_blocks[-1] += chunk

                if "```" in json_blocks[-1]:
                    json_found = False
                    splitted = json_blocks[-1].split("```", maxsplit=1)

                    if len(splitted) == 1:
                        json_blocks[-1] = splitted[0]
                    else:    
                        json_blocks[-1], remaining_chunk = splitted
                        consume_chunk(remaining_chunk)

        async for chunk, metadata in self.app.astream(
            {"user_input": text, "language": language},
            {"configurable": {"thread_id": self.thread_id}},

            # CAVEAT 1: This makes the workflow stream out all LLM responses. Only then do we
            # get a chunk object and metadata dict. But we need to skip all chunks from LLM
            # calls in intermediate nodes, since we only want to send back the result of the
            # final LLM call to the frontend.
            #
            # CAVEAT 2: All Message instances in the state will automatically be streamed
            # out to the client (as a diff, meaning all messages that haven't been sent already).
            # So don't buffer Message objects in the state if they are only internal.
            stream_mode="messages",
        ):
            if hasattr(chunk, "content") \
            and metadata["langgraph_node"] == "send_user_message_to_llm": # type: ignore
                consume_chunk(chunk.content) # type: ignore
                await callback("chat_reply", {"id": reply_id, "text": reply_text, "meta": metadata})
        
        for json_block in json_blocks:
            await callback("quiz", {"data": json.loads(json_block)})

_SYSTEM_PROMPT="""
# Procedure

You are ELISA - an interactive learning tutor who supports me in my learning and can create quizzes for me.
Please stick to the following procedure:

1. Introduce yourself and ask me what my name is.
2. Say hello to me. But please only once and then never again!
3. Ask me what subject I want to learn and how well I already know it.
4. Create suitable quiz questions and answers that are adapted to my level of knowledge.
5. Ask me if everything is clear or if you should give me some hints for the quiz.
   Also tell me that you will give detailed feedback after I answered all questions.
6. Later I will tell you my answers so that you can give me feedback.
7. At the end, ask me if I want you to create more quiz questions (maybe more difficult ones now),
   or if I want to learn a new topic.

If I decide in favour of a new topic or more quiz questions, go back to step 4: Creating the quiz questions.
Otherwise, politely say goodbye and offer that I can always come back for more.

# Quiz questions

The quiz questions should always be five multiple-choice questions with exactly four answers, of which exactly one
is always correct. The other three answers are therefore always wrong. Choose the questions and answers so that the
correct answer is not immediately obvious. Please format the quiz questions and answers as a JSON structure, as shown
in the following example:

```json
{{
    "subject": "Name of the selected topic",
    "level": "Difficulty of the quiz",
    "questions": [
        {{
            "question": "What does the abbreviation HTML stand for",
            "answers": ["Hypertext Modern Language", "Hypertext Markup Language", "Hypertext Many Languages", "Nothing"],
            "correct": 1,
        }}
    ]
}}
```

"correct" is the index (counted from zero) of the correct answer.

* Never repeat quiz questions and answers in natural language!
* Don't tell me that the quiz is in JSON format.
"""

_SUMMARY_PROMPT = """
# Summary of our conversation so far

This is a summary of our conversation to date as a reference for you: {summary}

Please don't repeat what we already discussed before, unless I am explicitly asking for it.
"""

_USER_MESSAGE = """
# Hints

Sometimes I will try to elicit the correct answer for the quiz, but you are not allowed to tell me.
Just give me hints or politely refuse to answer, if I try to cheat.

# My Question

{user_input}

# Language

Please reply in language: {language}
"""

_NEW_SUMMARY_MESSAGE = """
# Summarize Conversation

Please create a summary of our conversation so far. Next are the full details on what you and I said.
If you generated a quiz for me, please keep it for reference:

{buffer}

# Language

Please write the summary in the language: {language}

Focus on what we said last. If necessary shorten older interactions.
"""

_EXTEND_SUMMARY_MESSAGE = """
# Summarized Conversation

This is a summary of our conversation to date: {summary}

# Your Job

Please extend the summary by taking into account the following messages that we exchanged since then.
If you generated a quiz for me, please keep it for reference:

{buffer}

# Language

Please write the summary in the language: {language}
"""