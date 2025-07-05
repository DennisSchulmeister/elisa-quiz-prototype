# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from pydantic import BaseModel

class WebsocketMessage(BaseModel):
    """
    Base type for all messages exchanged via the websocket. The only convention is
    that it contains a string code with the message type. Depending on the code other
    keys will be present.
    """
    code: str
    """Message code for routing the message to the right handler"""

    jwt: str = ""
    """OpenID Connect access token (JWT)"""

    body: dict = {}
    """Message body (type depends on the message code)"""

    class Config:
        extra = "allow"