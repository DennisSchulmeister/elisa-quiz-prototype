# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__          import annotations
from datetime            import datetime
from pydantic            import BaseModel
from typing              import TYPE_CHECKING

from ...ai.models        import ActivityStates, AgentStates, ChatKey, ConversationMemory, MessageHistory, PersistenceStrategy
from ...auth.exceptions  import PermissionDenied
from ...database.user    import Chat, UserDatabase
from ._decorators        import handle_message, websocket_handler

if TYPE_CHECKING:
    from ...auth.user import User
    from ..parent     import ParentWebsocketHandler

class RenameChat(ChatKey):
    """
    Message body to change the title of a chat conversation.
    """
    title: str

class SaveChat(BaseModel):
    """
    Message body to move a full chat conversation from client to server,
    so that it is centrally saved on the server.
    """
    timestamp:   datetime
    title:       str
    persistence: PersistenceStrategy
    encrypt:     bool
    history:     MessageHistory
    memory:      ConversationMemory
    agents:      AgentStates
    activities:  ActivityStates

@websocket_handler
class UserHandler:
    """
    Websocket message handler for user data management.
    """
    def __init__(self, parent: ParentWebsocketHandler):
        """
        Initialize client-bound handler instance.
        """
        self.parent = parent
    
    @handle_message("get_chats", require_auth=True)
    async def handle_get_chats(self, user: User):
        """
        Read an overview list of all saved chat conversations of the user.
        """
        chats = await UserDatabase.get_chats(username=user.subject)
        await self.parent.send_message("get_chats_reply", {"chats": chats})
    
    @handle_message("get_chat", ChatKey, require_auth=True)
    async def handle_get_chat(self, key: ChatKey, user: User):
        """
        Get a single chat conversation with full data.
        """
        if not key.username == user.subject:
            raise PermissionDenied()
        
        chat = await UserDatabase.get_chat(key)

        if not chat:
            await self.parent.send_message("get_chat_reply")
        else:
            await self.parent.send_message("get_chat_reply", chat.model_dump())
    
    @handle_message("rename_chat", RenameChat, require_auth=True)
    async def handle_rename_chat(self, rename: RenameChat, user: User):
        """
        Change title of a chat conversation.
        """
        if not rename.username == user.subject:
            raise PermissionDenied()
        
        await UserDatabase.rename_chat(rename, title=rename.title)

    @handle_message("save_chat", SaveChat, require_auth=True)
    async def handle_save_chat(self, chat: SaveChat, user: User):
        """
        Save a previously client-persisted chat conversation on the server.
        The client must delete the chat in the local storage afterwards to
        avoid data inconsistencies. Not meant make single changes to a chat,
        because always the full history is transferred and saved.
        """
        _chat = Chat.model_validate({
            "username": user.subject,
            **chat.model_dump(),
        })

        await UserDatabase.save_chat(_chat)

    @handle_message("delete_chat", ChatKey, require_auth=True)
    async def handle_delete_chat(self, key: ChatKey, user: User):
        """
        Delete a chat conversation.
        """
        if not key.username == user.subject:
            raise PermissionDenied()

        await UserDatabase.delete_chat(key)