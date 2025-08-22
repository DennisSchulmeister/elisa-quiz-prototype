# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

class AgentRegistry:
    """
    Dynamic class registry for AI agents.
    """

    default_agent_code = "default-agent"
    """Code of the default agent to use when no more specialized agent is found"""

    @classmethod
    def get_all_agent_classes(cls):
        """
        Get all agent classes available to the top-level chat manager
        """
        from .choice.agent         import ChoiceAgent
        from .default.agent        import DefaultAgent
        from .exam_interview.agent import ExamInterviewAgent
        from .quiz.agent           import QuizAgent

        return [
            DefaultAgent,
            # ChoiceAgent,
            # ExamInterviewAgent,
            # QuizAgent,
        ]

    @classmethod
    def get_all_agents_prompt(cls):
        """
        Return a string that describes all available agents to the LLM.
        """
        result = "<available_agents>"

        for agent_class in cls.get_all_agent_classes():
            result += f"""
                <agent>
                    <agent_code>{agent_class.code}</agent_code>
                    <description>{agent_class.__doc__}</description>
                </agent>
            """
        
        result += "</available_agents>"
        return result