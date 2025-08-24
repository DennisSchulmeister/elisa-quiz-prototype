# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

from __future__ import annotations
from os         import environ
from typing     import override, TYPE_CHECKING
from ..shared   import ReadConfigMixin

if TYPE_CHECKING:
    from ._guard_rail      import GuardRailBase
    from ._agent           import AgentBase
    from ._agent_router    import AgentRouterBase
    from ._summarizer      import SummarizerBase
    from ._title_generator import TitleGeneratorBase

class AIRegistry(ReadConfigMixin):
    """
    Dynamic class registry for the summary generation strategy.
    """
    Agents:         list[type[AgentBase]]     = []
    GuardRails:     list[type[GuardRailBase]] = []
    AgentRouter:    type[AgentRouterBase]     = None    # type: ignore
    Summarizer:     type[SummarizerBase]      = None    # type: ignore
    TitleGenerator: type[TitleGeneratorBase]  = None    # type: ignore

    default_agent_code = "default"
    """Agent code of the default agent"""

    @override
    @classmethod
    def read_config(cls):
        """
        Read configuration values and find classes during server start-up.
        """
        cls._init_agents()
        cls._init_agent_router()
        cls._init_guard_rails()
        cls._init_summarizer()
        cls._init_title_generator()

    @classmethod
    def _init_agents(cls):
        from ._agents.choice         import ChoiceAgent
        from ._agents.default        import DefaultAgent
        from ._agents.exam_interview import ExamInterviewAgent
        from ._agents.quiz           import QuizAgent

        cls.Agents = [
            DefaultAgent,
            # ChoiceAgent,
            # ExamInterviewAgent,
            # QuizAgent,
        ]

        for agent_class in cls.Agents:
            agent_class.read_config()

    @classmethod
    def _init_agent_router(cls):
        strategy = environ.get("ELISA_AGENT_ROUTER", "default")

        if strategy == "default":
            from ._agent_routers.default import DefaultAgentRouter
            cls.AgentRouter = DefaultAgentRouter
        else:
            raise KeyError(f"ELISA_AGENT_ROUTER - Invalid value: {strategy}")

        cls.AgentRouter.read_config()

    @classmethod
    def _init_guard_rails(cls):
        guard_rails = environ.get("ELISA_GUARD_RAILS", "message_size, content_safety_llm")

        for guard_rail in guard_rails.split(","):
            guard_rail = guard_rail.strip()

            if guard_rail == "message_size":
                from ._guard_rails.message_size import MessageSizeGuardRail
                cls.GuardRails.append(MessageSizeGuardRail)
            elif guard_rail == "content_safety_llm":
                from ._guard_rails.content_safety_llm import ContentSafetyLLMGuardRail
                cls.GuardRails.append(ContentSafetyLLMGuardRail)
            else:
                raise KeyError(f"ELISA_GUARD_RAILS - Invalid value: {guard_rail}")
        
        for guard_rail_class in cls.GuardRails:
            guard_rail_class.read_config()


    @classmethod
    def _init_summarizer(cls):
        strategy   = environ.get("ELISA_SUMMARIZER", "default")
        keep_count = environ.get("ELISA_SUMMARIZER_KEEP", "10")

        if strategy == "default":
            from ._summarizers.default import DefaultSummarizer
            cls.Summarizer = DefaultSummarizer
        else:
            raise KeyError(f"ELISA_SUMMARIZER - Invalid value: {strategy}")
        
        try:
            cls.Summarizer.keep_count = int(keep_count)
        except ValueError:
            raise ValueError(f"ELISA_SUMMARIZER_KEEP - Must be integer: {keep_count}")
    
        cls.Summarizer.read_config()

    @classmethod
    def _init_title_generator(cls):
        strategy = environ.get("ELISA_TITLE_GENERATOR", "default")

        if strategy == "default":
            from ._title_generators.default import DefaultTitleGenerator
            cls.TitleGenerator = DefaultTitleGenerator
        else:
            raise KeyError(f"ELISA_TITLE_GENERATOR - Invalid value: {strategy}")
    
        cls.TitleGenerator.read_config()