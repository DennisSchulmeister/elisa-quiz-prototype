# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import os, typing

if typing.TYPE_CHECKING:
    from .base import GuardRailBase

class GuardRailRegistry:
    """
    Dynamic class registry for the title generation strategy.
    """
    GuardRails: "list[type[GuardRailBase]]" = []

    @classmethod
    def read_config(cls):
        """
        Find configured strategy during server startup.
        """
        guard_rails = os.environ.get("ELISA_GUARD_RAILS", "message_size, content_safety_llm")

        for guard_rail in guard_rails.split(","):
            guard_rail = guard_rail.strip()

            if guard_rail == "message_size":
                from .impl.message_size import MessageSizeGuardRail
                cls.GuardRails.append(MessageSizeGuardRail)
            elif guard_rail == "content_safety_llm":
                from .impl.content_safety_llm import ContentSafetyLLMGuardRail
                cls.GuardRails.append(ContentSafetyLLMGuardRail)
            else:
                raise KeyError(f"ELISA_GUARD_RAILS - Invalid value: {guard_rail}")
        
        for guard_rail_class in cls.GuardRails:
            guard_rail_class.read_config()