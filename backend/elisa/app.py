# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from contextlib           import asynccontextmanager
from dotenv               import load_dotenv
from fastapi              import FastAPI
from fastapi              import WebSocket

from .core.database       import init_database
from .core.websocket      import ParentWebsocketHandler
from .handlers.analytics  import AnalyticsHandler
from .handlers.chat       import ChatHandler
from .handlers.connection import ConnectionHandler
from .handlers.error      import ErrorHandler

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start-up code before handling requests
    load_dotenv()

    await init_database()

    ParentWebsocketHandler.add_handler(AnalyticsHandler)
    ParentWebsocketHandler.add_handler(ChatHandler)
    ParentWebsocketHandler.add_handler(ConnectionHandler)
    ParentWebsocketHandler.add_handler(ErrorHandler)

    # Now start handling requests
    yield

    # Shutdown code

app = FastAPI(lifespan=lifespan)

@app.websocket("/ws/chat")
async def chat_websocket(websocket: WebSocket):
    handler = ParentWebsocketHandler(websocket)
    await handler.run()