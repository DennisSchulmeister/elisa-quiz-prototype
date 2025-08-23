# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import os, typing

if typing.TYPE_CHECKING:
    from .base import SummarizerBase

class SummarizerRegistry:
    """
    Dynamic class registry for the summary generation strategy.
    """
    Summarizer: "type[SummarizerBase]" = None    # type: ignore

    @classmethod
    def read_config(cls):
        """
        Find configured strategy during server startup.
        """
        strategy   = os.environ.get("ELISA_SUMMARIZER", "default")
        keep_count = os.environ.get("ELISA_SUMMARIZER_KEEP", "10")

        if strategy == "default":
            from .impl.default import DefaultSummarizer
            cls.Summarizer = DefaultSummarizer
        else:
            raise KeyError(f"ELISA_SUMMARIZER - Invalid value: {strategy}")
        
        try:
            cls.Summarizer.keep_count = int(keep_count)
        except ValueError:
            raise ValueError(f"ELISA_SUMMARIZER_KEEP - Must be integer: {keep_count}")
    
        cls.Summarizer.read_config()