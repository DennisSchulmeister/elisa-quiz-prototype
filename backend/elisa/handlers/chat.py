# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from typeguard          import check_type

from ..agents.prototype import ChatMessage
from ..agents.prototype import EndActivityData
from ..agents.prototype import PersistedConversation
from ..agents.prototype import PrototypeAgent
from ..agents.prototype import StartActivityData
from ..core.decorators  import handle_message
from ..core.decorators  import websocket_handler
from ..core.websocket   import ParentWebsocketHandler
from ..core.websocket   import WebsocketMessage

class ChatInputMessage(WebsocketMessage):
    """
    Chat input from the user.
    """
    text: str

class ResumeConversationMessage(WebsocketMessage, PersistedConversation):
    """
    Persisted conversation to resume from a previous session.
    """

class EndActivityMessage(WebsocketMessage, EndActivityData):
    """
    Request for LLM feedback at the end of an activity.
    """

@websocket_handler
class ChatHandler:
    """
    Websocket message for chat conversations and LLM-based activities.
    """
    def __init__(self, parent: ParentWebsocketHandler):
        """
        Initialize client-bound handler instance.
        """
        self.parent     = parent
        self.chat_agent = PrototypeAgent(
            send_chat_message       = self.send_chat_message,
            send_start_activity     = self.send_start_activity,
            send_conversation_state = self.send_conversation_state,
        )
    
    def notify(self, key: str, value):
        """
        Receive notification from analytics handler, whether the user allows to
        track the learning topics.
        """
        if key == "record_learning_topics":
            self.chat_agent.set_record_learning_topic(value)

    @handle_message("start_conversation")
    async def handle_start_conversation(self, message: WebsocketMessage):
        """
        Reset conversation state to start a new conversation.
        """
        await self.chat_agent.start_conversation()

    @handle_message("resume_conversation")
    async def handle_resume_conversation(self, message: ResumeConversationMessage):
        """
        Resume previous conversation based on the received conversation state.
        Currently, conversations can only be resumed when they are persisted
        by the client and in a new session sent to the backend with this message,
        as we don't yet have server-side chat persistence.
        """
        await self.chat_agent.resume_conversation(message)

    @handle_message("chat_input")
    async def handle_chat_input(self, message: ChatInputMessage):
        """
        Feed chat input from user to the LLM and stream back the response.
        """
        check_type(message, ChatInputMessage)
        
        text     = message.get("text", "")
        language = message.get("language", "en")

        await self.chat_agent.invoke_with_new_user_message(text, language)
    
    @handle_message("end_activity")
    async def handle_end_activity(self, message: EndActivityMessage):
        """
        Feed activity result to the LLM to generate a feedback message.
        """
        await self.chat_agent.generate_feedback_for_activity(message)
    
    async def send_chat_message(self, message: ChatMessage):
        """
        Send a chat message to the client.
        """
        await self.parent.send_message("chat_message", message)
    
    async def send_start_activity(self, data: StartActivityData):
        """
        Send message to start an interactive activity to the client.
        """
        await self.parent.send_message("start_activity", data)

    async def send_conversation_state(self, data: PersistedConversation):
        """
        Send conversation state to the client, so that the state can be persisted
        and the conversation be resumed in a new session.
        """
        await self.parent.send_message("conversation_state", data)