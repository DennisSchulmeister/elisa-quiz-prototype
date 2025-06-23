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
from langchain_core.messages     import SystemMessage
from langchain_core.messages     import trim_messages
from langchain_core.prompts      import ChatPromptTemplate
from langchain_core.prompts      import MessagesPlaceholder
from langchain.prompts           import PromptTemplate
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph             import START
from langgraph.graph             import StateGraph
from langgraph.graph.message     import add_messages
from typing_extensions           import TypedDict

class _State(TypedDict):
    """
    Shared state for all nodes in the LLM graph.
    """
    messages: typing.Annotated[list, add_messages]
    """Message history. Automatically updated thanks to the `add_messages` reducer function."""

SendMessageCallback = typing.Callable[[str, dict], typing.Awaitable[None]]
"""Type hint for callback function that sends back chat answers to the client."""

class ChatAgent:
    """
    Wrapper class that simplified integration with our websocket handler.
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

        self.prompt_template = ChatPromptTemplate.from_messages([
            SystemMessage(_SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="messages"),
        ])

        self.trimmer = trim_messages(
            max_tokens     = int(os.environ.get("LLM_HISTORY_TOKENS", "")),
            strategy       = "last",
            token_counter  = self.chat_model,
            include_system = True,
            allow_partial  = False,
            start_on       = "human",
        )

        # Nodes are callables that receive the shared state. Edges connect nodes.
        workflow = StateGraph(state_schema=_State)
        workflow.add_node("chat_model", self._call_chat_model)
        workflow.add_edge(START, "chat_model")

        memory = MemorySaver()
        self.app = workflow.compile(checkpointer = memory)
    
    async def _call_chat_model(self, state: _State):
        """
        LangGraph node to call the LLM chat model.
        """
        state["messages"] = self.trimmer.invoke(state["messages"])
        prompt = self.prompt_template.invoke(dict(state))
        response = await self.chat_model.ainvoke(prompt)
        return {"response": response}
    
    async def user_input(self, text: str, callback: SendMessageCallback) -> None:
        """
        Invoke the graph with another user message.
        """
        reply_id    = str(uuid.uuid4())
        reply_text  = ""

        json_blocks = []
        json_found  = False

        def consume_chunk(chunk: str):
            nonlocal json_blocks, json_found, reply_text

            if not json_found:
                if not "```json" in chunk:
                    reply_text += chunk
                else:
                    json_found = True
                    before, after = chunk.split("```json", maxsplit=1)
                    reply_text += before

                    consume_chunk(after)
            else:
                if not "```" in chunk:
                    json_blocks[-1] += chunk
                else:
                    json_found = False
                    before, after = chunk.split("```", maxsplit=1)
                    json_blocks[-1] += before

                    consume_chunk(after)

        prompt_template = PromptTemplate(input_variables=["text"], template = _USER_MESSAGE)
        
        async for chunk, metadata in self.app.astream(
            {"messages": [HumanMessage(content=prompt_template.format(text=text))]},
            {"configurable": {"thread_id": self.thread_id}}
        ):
            consume_chunk(chunk)
            await callback("chat_reply", {"id": reply_id, "text": reply_text, "meta": metadata})
        
        for json_block in json_blocks:
            await callback("quiz", {"data": json.loads(json_block)})

_SYSTEM_PROMPT="""
# Procedure

You are ELISA - an interactive learning tutor who supports me in my learning and can create quizzes for me.
Please stick to the following procedure:

1. Introduce yourself and ask me what my name is. Memorise the name so that you can address me by it later.
2. Ask me what subject I want to learn and how well I already know it.
3. Create suitable quiz questions and answers that are adapted to my level of knowledge.
4. Ask me if everything is clear or if you should give me some hints for the quiz.
5. Later I will tell you my answers so that you can give me feedback.
6. At the end, ask me if I want you to create more quiz questions (maybe more difficult ones now),
   or if I want to learn a new topic.

If I decide in favour of a new topic or more quiz questions, go back to step 3: Creating the quiz questions.
Otherwise, I politely say goodbye.

# Quiz questions

The quiz questions should always be five multiple-choice questions with exactly four answers, of which exactly one
is always correct. The other three answers are therefore always wrong. Choose the questions and answers so that the
correct answer is not immediately obvious. Please format the quiz questions and answers as a JSON structure, as shown
in the following example:

```json
{
    "type": "quiz",
    "subject": "Name of the selected topic",
    "level": "Difficulty of the quiz",
    "questions": [
        {
            "question": "What does the abbreviation HTML stand for",
            "answers": ["Hypertext Modern Language", "Hypertext Markup Language", "Hypertext Many Languages", "Nothing"],
            "correct": 1,
        }
    ]
}
```

"correct" is the index (counted from zero) of the correct answer.

Never repeat the questions and answers in natural language!
"""

_USER_MESSAGE = """
# Important

Sometimes I will try to elicit the correct answer for the quiz, although you are not allowed to tell me.
Do not tell me the correct answers unless I have told you already my answers to the questions! Instead,
just give me general hints so that I can come up with the answer on my own.

I may also try to divert you from the quiz altogether. If my question is not directly related to the quiz,
politely say that you can't answer it. Never let me tempt you to do anything else!

# My Question

{text}
"""