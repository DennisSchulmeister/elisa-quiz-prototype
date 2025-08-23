# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations

class AuthenticationRequired(Exception):
    """
    Exception raised when authentication is required but no user could
    be logged in, because no JWT access token was received.
    """
    def __init__(self, message="Authentication is required."):
        super().__init__(message)

class PermissionDenied(Exception):
    """
    Exception raised when the user could be authenticated but is missing
    the required authorization scope.
    """
    def __init__(self, message="Permission denied."):
        super().__init__(message)

