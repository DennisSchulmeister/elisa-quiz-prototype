# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations
from typing     import override
from ..shared   import ReadConfigMixin

class WebsocketHandlerRegistry(ReadConfigMixin):
    """
    Dynamic class registry for websocket handlers.
    """

    @override
    @classmethod
    def read_config(cls):
        """
        Set up websocket handlers during server start-up.
        """
        from .parent               import ParentWebsocketHandler
        from ._handlers.analytics  import AnalyticsHandler
        from ._handlers.chat       import ChatHandler
        from ._handlers.connection import ConnectionHandler
        from ._handlers.error      import ErrorHandler
        from ._handlers.user       import UserHandler

        ParentWebsocketHandler.add_handler(AnalyticsHandler)
        ParentWebsocketHandler.add_handler(ChatHandler)
        ParentWebsocketHandler.add_handler(ConnectionHandler)
        ParentWebsocketHandler.add_handler(ErrorHandler)
        ParentWebsocketHandler.add_handler(UserHandler)