# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from ..ai.callback      import ChatAgentCallbackABC
from ..ai.chat          import ChatAgent
from ..core.decorators  import handle_message
from ..core.decorators  import websocket_handler
from ..core.typing      import check_type
from ..core.websocket   import ParentWebsocketHandler
from ..core.websocket   import WebsocketMessage

# class StartConversationMessage(WebsocketMessage):
#     """
#     Start new conversation and trigger welcome message by LLM.
#     """
#     language: str
# 
# class ResumeConversationMessage(WebsocketMessage, PersistedConversation):
#     """
#     Persisted conversation to resume from a previous session.
#     """
# 
# class ChatInputMessage(WebsocketMessage):
#     """
#     Chat input from the user.
#     """
#     text: str
#     language: str
# 
# class UpdateActivityMessage(WebsocketMessage, UpdateActivityData):
#     """
#     Message to exchange the updated internal state of a currently running
#     interactive activity between client and server.
#     """

@websocket_handler
class ChatHandler(ChatAgentCallbackABC):
    """
    Websocket message for chat conversations and interactive activities.
    """
    def __init__(self, parent: ParentWebsocketHandler):
        """
        Initialize client-bound handler instance.
        """
        self.parent     = parent
        self.chat_agent = ChatAgent(self)
    
    def notify(self, key: str, value):
        """
        Receive notification from analytics handler, whether the user allows to
        track the learning topics.
        """
        if key == "record_learning_topics":
            self.chat_agent.set_record_learning_topic(value)




#     @handle_message("start_conversation")
#     async def handle_start_conversation(self, message: StartConversationMessage):
#         """
#         Reset conversation state to start a new conversation.
#         """
#         check_type(message, StartConversationMessage)
#         await self.chat_agent.start_conversation(message["language"])
# 
#     @handle_message("resume_conversation")
#     async def handle_resume_conversation(self, message: ResumeConversationMessage):
#         """
#         Resume previous conversation based on the received conversation state.
#         Currently, conversations can only be resumed when they are persisted
#         by the client and in a new session sent to the server with this message,
#         as we don't yet have server-side chat persistence.
#         """
#         await self.chat_agent.resume_conversation(message)
# 
#     @handle_message("chat_message")
#     async def handle_chat_message(self, message: ChatInputMessage):
#         """
#         Feed chat input from user to the LLM and stream back the response.
#         """
#         check_type(message, ChatInputMessage)
#         
#         text     = message.get("text")
#         language = message.get("language")
# 
#         await self.chat_agent.process_chat_message(text, language)
#     
#     @handle_message("update_activity")
#     async def handle_update_activity(self, message: UpdateActivityMessage):
#         """
#         Receive new data for a currently running activity. This message is sent by
#         the client for activities, where the internal state of the activity is
#         mutated by the client usually due to a user interaction. But also the
#         server can mutate the internal state and send a similar message.
#         """
#         await self.chat_agent.process_activity_update(message)
#     
#     #override
#     async def send_chat_message(self, message: ChatMessage):
#         """
#         Send a chat message to the client.
#         """
#         await self.parent.send_message("chat_message", message)
#     
#     #override
#     async def send_start_activity(self, data: StartActivityData):
#         """
#         Send message to start an interactive activity to the client.
#         """
#         await self.parent.send_message("start_activity", data)
#     
#     #override
#     async def send_update_activity(self, data: UpdateActivityData):
#         """
#         Send updated activity state from server to client.
#         """
#         await self.parent.send_message("update_activity")
# 
#     #override
#     async def send_conversation_state(self, data: PersistedConversation):
#         """
#         Send conversation state to the client, so that the state can be persisted
#         and the conversation be resumed in a new session.
#         """
#         await self.parent.send_message("conversation_state", data)