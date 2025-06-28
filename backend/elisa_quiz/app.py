# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from dotenv          import load_dotenv
from fastapi         import FastAPI
from fastapi         import WebSocket
from .core.websocket import ParentWebsocketHandler

load_dotenv()
app = FastAPI()

@app.websocket("/ws/chat")
async def chat_websocket(websocket: WebSocket):
    handler = ParentWebsocketHandler(websocket)
    await handler.run()