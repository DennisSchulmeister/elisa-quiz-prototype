# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations

class ReadConfigMixin:
    """
    Mixin class that provides a class method to read and validate configuration
    values during server-startup.
    """

    @classmethod
    def read_config(cls):
        """
        Read and validate configuration values during server start-up, by checking the
        relevant environment variables. Raises an exception for invalid configuration values.
        """