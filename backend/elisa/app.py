# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from contextlib                    import asynccontextmanager
from fastapi                       import FastAPI
from fastapi                       import WebSocket

from .ai.chat                      import ChatAgent
from .auth.user                    import User
from .websocket.parent             import ParentWebsocketHandler
from .websocket.analytics.handler  import AnalyticsHandler
from .websocket.chat.handler       import ChatHandler
from .websocket.connection.handler import ConnectionHandler
from .websocket.error.handler      import ErrorHandler
from .websocket.user.handler       import UserHandler

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start-up code before handling requests
    ChatAgent.create_client()
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