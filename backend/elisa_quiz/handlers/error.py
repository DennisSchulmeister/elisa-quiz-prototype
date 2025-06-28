# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from ..core.websocket import AbstractWebsocketHandler
from ..core.websocket import ParentWebsocketHandler
from ..core.websocket import WebsocketMessage

class ErrorHandler(AbstractWebsocketHandler):
    """
    Websocket message handler for crash reports and stack traces.
    """