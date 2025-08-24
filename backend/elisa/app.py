# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__            import annotations
from contextlib            import asynccontextmanager
from fastapi               import FastAPI
from typing                import TYPE_CHECKING

from .ai.assistant         import AIAssistant
from .ai.registry          import AIRegistry
from .auth.user            import User
from .websocket.parent     import ParentWebsocketHandler
from .websocket.registry   import WebsocketHandlerRegistry

if TYPE_CHECKING:
    from fastapi import WebSocket

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start-up code before handling requests    
    AIAssistant.read_config()    
    AIRegistry.read_config()
    User.read_config()
    WebsocketHandlerRegistry.read_config()

    # Now start handling requests
    yield

    # Shutdown code

app = FastAPI(lifespan=lifespan)

@app.websocket("/")
async def chat_websocket(websocket: WebSocket):
    handler = ParentWebsocketHandler(websocket)
    await handler.run()