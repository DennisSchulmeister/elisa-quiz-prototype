# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from typing                import override
from typing                import TYPE_CHECKING

from ...ai.agent.types     import ActivityUpdate
from ...ai.types           import StartChat
from ...ai.callback        import ChatAgentCallback
from ...ai.chat            import ChatManager
from ...ai.types           import UserChatMessage
from ..decorators          import handle_message
from ..decorators          import websocket_handler
from .types                import ChangeLanguage
from .types                import StartActivity

if TYPE_CHECKING:
    from ...ai.agent.types import AgentUpdate
    from ...ai.types       import AgentChatMessage
    from ...ai.types       import MemoryUpdate
    from ...auth.user      import User
    from ..parent          import ParentWebsocketHandler

@websocket_handler
class ChatHandler(ChatAgentCallback):
    """
    Websocket message for chat conversations and interactive activities.
    """
    def __init__(self, parent: ParentWebsocketHandler):
        """
        Initialize client-bound handler instance.
        """
        self.parent  = parent
        self.manager = ChatManager(self)
    
    def notify(self, key: str, value):
        """
        Receive notification from analytics handler, whether the user allows to
        track the learning topics.
        """
        if key == "record_learning_topics":
            self.manager.set_record_learning_topic(value)

    @handle_message("start_chat", StartChat)
    async def handle_start_chat(self, start: StartChat, user: User, **kwargs):
        """
        Start new chat conversation or resume previous conversation. To resume an
        old conversation, the client sends its thread id. If the chat history is
        saved on the client, it also sends the short-term memory. Otherwise it is
        assumed, that the history is saved by the server.
        """
        await self.manager.start_chat(start, user)

    @handle_message("user_chat_message", UserChatMessage)
    async def handle_user_chat_message(self, msg: UserChatMessage, user: User, **kwargs):
        """
        Process chat message sent by the user.
        """
        await self.manager.process_chat_message(msg, user)
    
    @handle_message("start_activity", StartActivity)
    async def handle_start_activity(self, start: StartActivity, user: User, **kwargs):
        """
        Start or resume an interactive activity.
        """
        await self.manager.start_activity(start.id)
    
    @handle_message("activity_update", ActivityUpdate)
    async def handle_activity_update(self, update: ActivityUpdate, user: User, **kwargs):
        """
        Send activity update to the owning AI agent after modification by the user.
        """
        update.origin = "user"
        await self.manager.propagate_activity_update(update)

    @handle_message("change_language", ChangeLanguage)
    async def handle_change_language(self, change: ChangeLanguage, **kwargs):
        """
        Remember new language for AI generated chat messages.
        """
        self.manager.set_language(change.language)

    @override
    async def send_agent_chat_message(self, msg: AgentChatMessage, **kwargs):
        """
        Send an agent chat message to the client.
        """
        await self.parent.send_message("agent_chat_message", msg.model_dump())
    
    @override
    async def send_memory_update(self, update: MemoryUpdate, **kwargs):
        """
        Send conversation memory update to the client, when the client signaled
        that it wants to persist the conversation.
        """
        await self.parent.send_message("memory_update", update.model_dump())
    
    @override
    async def send_agent_update(self, update: AgentUpdate, **kwargs):
        """
        Send agent state update to the client, when the client signaled that
        it wants to persist the conversation.
        """
        await self.parent.send_message("agent_update", update.model_dump())

    @override
    async def send_activity_update(self, update: ActivityUpdate, **kwargs):
        """
        Send activity update to the client after modification by an agent.
        """
        await self.parent.send_message("activity_update", update.model_dump())
