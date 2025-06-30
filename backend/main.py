#!/usr/bin/env python

# Elisa: AI Learning Assistant
# © 2025 Dennis Schulmeister-Zimolong <dennis@wpvs.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

import argparse, dotenv, os, uvicorn

if __name__ == "__main__":
    dotenv.load_dotenv()

    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default=os.getenv("UVICORN_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("UVICORN_PORT", 8000)))
    parser.add_argument("--reload", action="store_true", default=os.getenv("UVICORN_RELOAD", "false").lower() == "true")
    args = parser.parse_args()

    uvicorn.run("elisa.app:app", host=args.host, port=args.port, reload=args.reload)