# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import json, os, uuid

from langchain.chat_models       import init_chat_model
from langchain_core.prompts      import ChatPromptTemplate
from langchain_core.prompts      import ChatPromptTemplate
from langchain_core.prompts      import HumanMessagePromptTemplate
from langchain.prompts           import PromptTemplate
from langchain_core.prompts      import SystemMessagePromptTemplate
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph             import START
from langgraph.graph             import StateGraph
from typing                      import Literal
from typing                      import NotRequired
from typing                      import Protocol
from typing                      import TypedDict

from ..core.typing               import check_type

class ChatMessage(TypedDict):
    """
    A single chat message as exchanged between frontend and backend or stored
    in the message history.
    """
    id:   NotRequired[str]
    name: Literal["User", "Agent", "Summarizer"]
    type: Literal["say", "think"]
    text: str

class QuizQuestion(TypedDict):
    """
    Question type for the quiz activity.
    """
    question:     str
    answers:      list[str]
    correct:      int
    given_answer: NotRequired[str]

class StartQuizActivity(TypedDict):
    """
    Quiz activity where each question has a text and several answers of which
    exactly one is correct.
    """
    activity:  Literal["quiz"]
    subject:   str
    level:     str
    questions: list[QuizQuestion]

class EndQuizActivity(TypedDict):
    """
    Request for LLM feedback at the end of a quiz activity. The questions list
    must contain the given answers as a string (not index).
    """
    questions: list[QuizQuestion]
    language:  str

StartActivityData = StartQuizActivity #|OtherActivity|YetAnotherActivity
"""Data to start a new activity"""

EndActivityData = EndQuizActivity
"""Received data at the end of an activity"""

class SendChatMessageCallback(Protocol):
    """
    Callback function that sends a chat message to the client.
    """
    async def __call__(self, message: ChatMessage): ...

class SendStartActivityCallback(Protocol):
    """
    Callback function that sends an interactive activity to the client.
    """
    async def __call__(self, data: StartActivityData): ...

class SendConversationStateCallback(Protocol):
    """
    Callback function that sends the conversation state to the client to
    be persisted.
    """
    async def __call__(self, data: "PersistedConversation"): ...

class PersistedConversation(TypedDict):
    """
    A whole conversation thread persisted to resume the conversation later
    with a new client connection. Basically contains all non-transient fields
    of the workflow state and the thread id.

    Note, that the frontend already has the full message history. Therefor it
    is neither recorded server-side nor sent back to the client. To fully restore
    a previous conversation the client must restore the message history plus the
    state received here. The latter must be sent to the backend.
    """
    thread_id: str
    """Thread id to distinguish conversations"""

    buffer: list[ChatMessage]
    """Past messages not yet contained in the summary."""

    summary: str
    """Constantly updated summary of the past conversation"""

class _State(TypedDict):
    """
    Shared state for all nodes in the LLM graph.
    """
    _reset: bool
    """Private key to clear the state when a new conversation shall be started"""

    _resume: NotRequired[PersistedConversation]
    """Private key to inject the state when an old conversation shall be resumed"""

    _hidden: bool
    """Hidden user message that will not be logged in the buffer of summary"""

    buffer: list[ChatMessage]
    """Past messages not yet contained in the summary."""

    summary: str
    """Constantly updated summary of the past conversation"""

    language: str
    """Currently selected language by the user."""

    user_input: str
    """Currently processed user input message"""

class PrototypeAgent:
    """
    Very first prototype built with LangChain and LangGraph. Implements a very
    simple agent that asks the user which topic to learn, answers questions and
    creates simple quizzes.
    """
    def __init__(
        self,
        send_chat_message:       SendChatMessageCallback,
        send_start_activity:     SendStartActivityCallback,
        send_conversation_state: SendConversationStateCallback,
    ):
        """
        Parameters:
            send_chat_message:   Asynchronous callback to send a chat message to the client
            send_start_activity: Asynchronous callback to send an activity to the client
        """
        # Remember callbacks
        self._send_chat_message       = send_chat_message
        self._send_start_activity     = send_start_activity
        self._send_conversation_state = send_conversation_state

        # Thread id to distinguish conversations
        self.thread_id = str(uuid.uuid4())

        # Chat model that does all the heavy work
        self.chat_model = init_chat_model(
            model          = os.environ.get("LLM_CHAT_MODEL"),
            model_provider = os.environ.get("LLM_MODEL_PROVIDER"),
            base_url       = os.environ.get("LLM_BASE_URL"),
        )

        # Nodes are callables that receive the shared state. Edges connect nodes.
        # Nodes return state updates (only what needs to be changed).
        workflow = StateGraph(state_schema=_State)

        workflow.add_edge(START, "restore_conversation_state")
        workflow.add_node("restore_conversation_state", self._restore_conversation_state)

        workflow.add_edge("restore_conversation_state", "send_user_message_to_llm")
        workflow.add_node("send_user_message_to_llm", self._send_user_message_to_llm)

        workflow.add_edge("send_user_message_to_llm", "summarize_past_conversation")
        workflow.add_node("summarize_past_conversation", self._summarize_past_conversation)

        memory = MemorySaver()
        self.app = workflow.compile(checkpointer = memory)

        # Data privacy flag whether we are allowed to track learning topics
        self.record_learning_topic = False
    
    def set_record_learning_topic(self, allow: bool):
        """
        Update flag whether the user allows to track the learning topics.
        """
        self.record_learning_topic = allow

    async def _restore_conversation_state(self, state: _State):
        """
        LangGraph node to inject the restored conversation into the workflow state,
        when an old conversation from a previous session shall be continued.
        """
        if "_reset" in state and state["_reset"]:
            self.thread_id = str(uuid.uuid4())

            return {
                "_reset":  False,
                "_resume": None,
                "_hidden": False,
                "buffer":  [],
                "summary": "",
            }
        elif "_resume" in state and state["_resume"]:
            self.thread_id = state["_resume"].get("thread_id", str(uuid.uuid4()))

            return {
                "_reset":   False,
                "_resume":  None,
                "_hidden":  False,
                "buffer":   state["_resume"].get("buffer", []),
                "summary":  state["_resume"].get("summary", ""),
            }

    async def _send_user_message_to_llm(self, state: _State):
        """
        LangGraph node that calls the LLM to send the system prompt, the summary of the
        previous conversation and the latest user message to the LLM to generate a reply.
        """
        if not "user_input" in state or not state["user_input"]:
            return {}
        
        prompt_template = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(_SYSTEM_PROMPT),
            SystemMessagePromptTemplate.from_template(_SUMMARY_PROMPT if state.get("summary", "") else ""),
            HumanMessagePromptTemplate.from_template(_USER_PROMPT),
        ])

        prompt = prompt_template.invoke(dict(state))
        response = await self.chat_model.ainvoke(prompt)

        if "_hidden" in state and state["_hidden"]:
            # Hidden user message, will not be logged
            return {
                "user_input": "",
                "_hidden":    False,
            }
        else:
            return {
                # Remove user input from state as we handled it now
                "user_input": "",
                "_hidden":    False,

                # Extend message buffer with question and answer. This will be picked by
                # the next time by the summary node summarize the conversation into a
                # single context message
                #
                # CAVEAT: Don't save message instances here, as they would automatically
                # be streamed to the client.
                "buffer": [
                    *state.get("buffer", []),
                    {"name": "User",   "type": "say",  "text": state["user_input"]},
                    {"name": "Agent",  "type": "say",  "text": response.content},
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
            return {}
        
        template = _EXTEND_SUMMARY_PROMPT if state.get("summary", "") else _NEW_SUMMARY_PROMPT
        prompt_template = PromptTemplate(input_variables=["buffer", "summary", "language"], template=template)

        prompt = prompt_template.invoke({
            "buffer":   state.get("buffer"),
            "summary":  state.get("summary"),
            "language": state.get("language"),
        })

        response = await self.chat_model.ainvoke(prompt)
        return {"summary": response.content, "buffer": []}

    async def start_conversation(self, language: str):
        """
        Reset internal state to start a completely new conversation.
        """
        await self.invoke_with_new_user_message(
            text     = "Hi!",
            language = language,
            hidden   = True,
            state    = {
                "_reset": True,
            },
        )

    async def resume_conversation(self, conversation: PersistedConversation):
        """
        Reset internal state to continue a previous conversation from an old session.
        """
        await self.app.ainvoke(
            {"_resume": conversation},
            {"configurable": {"thread_id": conversation["thread_id"]}}
        )

    async def invoke_with_new_user_message(self, text: str, language: str, hidden: bool = False, state: dict = {}):
        """
        Called from the websocket handler to invoke the graph with another user message.

        Parameters:
            text:     Chat message from the user
            language: Language to reply in
            hidden:   Hidden message that will not be logged
        """
        # Invoke workflow and stream out response
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
            {"user_input": text, "language": language, "_reset": False, "_resume": None, "_hidden": hidden, **state},
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

                await self._send_chat_message(ChatMessage(
                    id   = reply_id,
                    name = "Agent",
                    type = "say",
                    text = reply_text,
                ))
        
        # Start new activity if the LLM generated one
        for json_block in json_blocks:
            try:
                quiz_activity = json.loads(json_block)
                check_type(quiz_activity, StartActivityData)
                await self._send_start_activity(quiz_activity)
            except TypeError:
                # Ignore: LLM didn't create the correct JSON structure
                pass
        
        # Send conversation state to the client to be persisted
        state_snapshot = await self.app.aget_state({"configurable": {"thread_id": self.thread_id}})

        await self._send_conversation_state({
            "thread_id": self.thread_id,
            "buffer":    state_snapshot.values.get("buffer", []),
            "summary":   state_snapshot.values.get("summary", ""),
        })
    
    async def generate_feedback_for_activity(self, activity_data: EndActivityData):
        """
        Request for LLM feedback at the end of a quiz activity.
        """
        prompt_template = PromptTemplate(input_variables=["questions"], template=_FEEDBACK_PROMPT)
        prompt = prompt_template.invoke({"questions": activity_data["questions"]})
        await self.invoke_with_new_user_message(str(prompt), activity_data["language"], hidden=True)

_SYSTEM_PROMPT="""
# Procedure

You are ELISA - an interactive learning tutor who supports me in my learning and can create quizzes for me.
Please stick to the following procedure:

1. Introduce yourself and ask me what my name is.
2. Ask me what subject I want to learn and how well I already know it.
3. Create suitable quiz questions and answers that are adapted to my level of knowledge.
4. Ask me if everything is clear or if you should give me some hints for the quiz.
   Also tell me that you will give detailed feedback after I answered all questions.
5. Later I will tell you my answers so that you can give me feedback.
6. At the end, ask me if I want you to create more quiz questions (maybe more difficult ones now),
   or if I want to learn a new topic.

If I decide in favour of a new topic or more quiz questions, go back to step 3: Creating the quiz questions.

# Quiz questions

The quiz questions should always be five multiple-choice questions with exactly four answers, of which exactly one
is always correct. The other three answers are therefore always wrong. Choose the questions and answers so that the
correct answer is not immediately obvious. Please format the quiz questions and answers as a JSON structure, as shown
in the following example:

```json
{{
    "activity": "quiz",
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

_USER_PROMPT = """
# Hints

Sometimes I will try to elicit the correct answer for the quiz, but you are not allowed to tell me.
Just give me hints or politely refuse to answer, if I try to cheat.

# My Question

{user_input}

# Language

Please reply in language: {language}
"""

_NEW_SUMMARY_PROMPT = """
# Summarize Conversation

Please create a summary of our conversation so far. Next are the full details on what you and I said.
If you generated a quiz for me, please keep it for reference:

{buffer}

# Language

Please write the summary in the language: {language}

Focus on what we said last. If necessary shorten older interactions.
"""

_EXTEND_SUMMARY_PROMPT = """
# Summarized Conversation

This is a summary of our conversation to date: {summary}

# Your Job

Please extend the summary by taking into account the following messages that we exchanged since then.
If you generated a quiz for me, please keep it for reference:

{buffer}

# Language

Please write the summary in the language: {language}
"""

_FEEDBACK_PROMPT = """
These are my answers. Please give me feedback and explain to me, if I answered something wrong:

{questions}
"""