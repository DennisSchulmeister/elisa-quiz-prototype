# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import os, typing

if typing.TYPE_CHECKING:
    from .base import AgentRouterBase

class AgentRouterRegistry:
    """
    Dynamic class registry for the agent routing strategy.
    """
    AgentRouter: "type[AgentRouterBase]" = None    # type: ignore

    @classmethod
    def read_config(cls):
        """
        Find configured strategy during server startup.
        """
        strategy = os.environ.get("ELISA_AGENT_ROUTER", "default")

        if strategy == "default":
            from .default.router import DefaultAgentRouter
            cls.AgentRouter = DefaultAgentRouter
        else:
            raise KeyError(f"ELISA_AGENT_ROUTER - Invalid value: {strategy}")