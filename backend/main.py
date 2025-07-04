#!/usr/bin/env python

# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import argparse, dotenv, os, uvicorn
from uvicorn.config import LOGGING_CONFIG

if __name__ == "__main__":
    dotenv.load_dotenv()

    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default=os.getenv("ELISA_LISTEN_IP", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("ELISA_LISTEN_PORT", 8000)))
    parser.add_argument("--reload", action="store_true", default=os.getenv("ELISA_HOT_RELOAD", "false").lower() == "true")
    args = parser.parse_args()

    LOGGING_CONFIG["formatters"]["default"]["fmt"] = "%(asctime)s  %(levelprefix)s %(message)s"

    uvicorn.run(
        app        = "elisa.app:app",
        host       = args.host,
        port       = args.port,
        reload     = args.reload,
    )