# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__         import annotations
from typing             import override

from ...ai.agent.types  import ActivityUpdate, AgentUpdate
from ...ai.assistant    import AIAssistant
from ...ai.callback     import ChatAgentCallback
from ...ai.types        import AssistantChatMessage, MemoryUpdate, UserChatMessage
from ...auth.exceptions import PermissionDenied
from ...auth.user       import User
from ..decorators       import handle_message, websocket_handler
from ..parent           import ParentWebsocketHandler
from .types             import ChangeLanguage, StartActivity, StartChat

@websocket_handler
class ChatHandler(ChatAgentCallback):
    """
    Websocket message for chat conversations and interactive activities.
    """
    def __init__(self, parent: ParentWebsocketHandler):
        """
        Initialize client-bound handler instance.
        """
        self._parent = parent
        self._assistant: AIAssistant | None = None
    
    def notify(self, key: str, value):
        """
        Receive notification from analytics handler, whether the user allows to
        track the learning topics.
        """
        if self._assistant and key == "record_learning_topics":
            self._assistant.record_learning_topic = value

    @handle_message("start_chat", StartChat)
    async def handle_start_chat(self, start: StartChat, user: User, **kwargs):
        """
        Start new chat conversation or resume previous conversation.
        """
        if start.username and not start.username == user.subject:
            raise PermissionDenied()
        
        self._assistant = await AIAssistant.create(
            callback    = self,
            user        = user,
            thread_id   = start.thread_id,
            persistence = start.persistence,
            state       = start.state,
        )

    @handle_message("user_chat_message", UserChatMessage)
    async def handle_user_chat_message(self, msg: UserChatMessage, user: User, **kwargs):
        """
        Process chat message sent by the user.
        """
        if self._assistant:
            await self._assistant.process_user_chat_message(msg, user)
    
    @handle_message("start_activity", StartActivity)
    async def handle_start_activity(self, start: StartActivity, user: User, **kwargs):
        """
        Start or resume an interactive activity.
        """
        if self._assistant:
            await self._assistant.start_activity(start.id)
    
    @handle_message("activity_update", ActivityUpdate)
    async def handle_activity_update(self, update: ActivityUpdate, user: User, **kwargs):
        """
        Send activity update to the owning AI agent after modification by the user.
        """
        if self._assistant:
            await self._assistant.propagate_activity_update(update)

    @handle_message("change_language", ChangeLanguage)
    async def handle_change_language(self, change: ChangeLanguage, **kwargs):
        """
        Remember new language for AI generated chat messages.
        """
        if self._assistant:
            self._assistant.language = change.language

    @override
    async def send_assistant_chat_message(self, msg: AssistantChatMessage, **kwargs):
        """
        Send an assistant chat message to the client.
        """
        await self._parent.send_message("assistant_chat_message", msg.model_dump())
    
    @override
    async def send_memory_update(self, update: MemoryUpdate, **kwargs):
        """
        Send conversation memory update to the client, when the client signaled
        that it wants to persist the conversation.
        """
        await self._parent.send_message("memory_update", update.model_dump())
    
    @override
    async def send_agent_update(self, update: AgentUpdate, **kwargs):
        """
        Send agent state update to the client, when the client signaled that
        it wants to persist the conversation.
        """
        await self._parent.send_message("agent_update", update.model_dump())

    @override
    async def send_activity_update(self, update: ActivityUpdate, **kwargs):
        """
        Send activity update to the client after modification by an agent.
        """
        await self._parent.send_message("activity_update", update.model_dump())