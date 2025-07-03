# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from ...ai.activity.types import ActivityTransaction
from ...ai.callback       import ChatAgentCallback
from ...ai.chat           import ChatAgent
from ...ai.types          import AgentChatMessage
from ...ai.types          import MemoryTransaction
from ...ai.types          import UserChatMessage
from ..decorators         import handle_message
from ..decorators         import websocket_handler
from ..parent             import ParentWebsocketHandler

@websocket_handler
class ChatHandler(ChatAgentCallback):
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

    @handle_message("start_chat", None)
    async def handle_start_chat(self, message, **kwargs):
        """
        """

    @handle_message("resume_chat", None)
    async def handle_resume_chat(self, message, **kwargs):
        """
        """

    @handle_message("user_chat_message", UserChatMessage)
    async def handle_user_chat_message(self, message: UserChatMessage, **kwargs):
        """
        """
    
    @handle_message("activity_transaction", ActivityTransaction)
    async def handle_activity_transaction(self, tx: ActivityTransaction, **kwargs):
        """
        """

    #@override
    async def send_agent_chat_message(self, message: AgentChatMessage, **kwargs):
        """
        Send an agent chat message to the client.
        """
        await self.parent.send_message("agent_chat_message", message.model_dump())
    
    #@override
    async def send_memory_transaction(self, tx: MemoryTransaction, **kwargs):
        """
        Send conversation memory update to the client, when the client signaled
        that it wants to persist the conversation.
        """
        await self.parent.send_message("memory_transaction", tx.model_dump())
    
    #@override
    async def send_activity_transaction(self, tx: ActivityTransaction, **kwargs):
        """
        Send activity update to the client, when it was modified by the agent.
        """
        await self.parent.send_message("activity_transaction", tx.model_dump())


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