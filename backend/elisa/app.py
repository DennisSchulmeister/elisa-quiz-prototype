# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations

from contextlib                    import asynccontextmanager
from fastapi                       import FastAPI
from typing                        import TYPE_CHECKING

from .ai.assistant                 import AIAssistant
from .ai.guard.registry            import GuardRailRegistry
from .ai.router.registry           import AgentRouterRegistry
from .ai.summary.registry          import SummarizerRegistry
from .ai.title.registry            import TitleGeneratorRegistry
from .auth.user                    import User
from .websocket.parent             import ParentWebsocketHandler
from .websocket.analytics.handler  import AnalyticsHandler
from .websocket.chat.handler       import ChatHandler
from .websocket.connection.handler import ConnectionHandler
from .websocket.error.handler      import ErrorHandler
from .websocket.user.handler       import UserHandler

if TYPE_CHECKING:
    from fastapi import WebSocket

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start-up code before handling requests    
    AIAssistant.read_config()
    
    AgentRouterRegistry.read_config()
    GuardRailRegistry.read_config()
    SummarizerRegistry.read_config()
    TitleGeneratorRegistry.read_config()
    User.read_config()

    ParentWebsocketHandler.add_handler(AnalyticsHandler)
    ParentWebsocketHandler.add_handler(ChatHandler)
    ParentWebsocketHandler.add_handler(ConnectionHandler)
    ParentWebsocketHandler.add_handler(ErrorHandler)
    ParentWebsocketHandler.add_handler(UserHandler)

    # Now start handling requests
    yield

    # Shutdown code

app = FastAPI(lifespan=lifespan)

@app.websocket("/")
async def chat_websocket(websocket: WebSocket):
    handler = ParentWebsocketHandler(websocket)
    await handler.run()