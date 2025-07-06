Developer Notes for ELISA: AI Learning Tutor
============================================

This document serves as a cheat sheet for developers to get started quickly. There are no
fancy things -- if you already know Python, Poetry, NPM, LangChain, FastAPI, … 🥸 But finding
the right information might not be easy when working with so much different technology. This
document tries to summarize a few things.

1. [Quick Start](#quick-start)
1. [Technology Choices](#technology-choices)
1. [Poetry Package Management](#poetry-package-management)
1. [NPM and esbuild](#npm-and-esbuild)
1. [Building the Distribution Package](#building-the-distribution-package)
1. [Testing the Websocket Communication](#testing-the-websocket-communication)

Quick Start
-----------

The following tools must be available on your development machine:

* Python
* Node.js

Then you can install all dependent libraries:

```sh
cd backend
poetry install

cd ../frontend
npm install

cd ..
npm install
```

From the root of the repository you can run the following command to start the frontend
and backend:

```sh
npm run start
```

This will start a development setup with the following things:

* Uvicorn webserver in watch mode (listening on [localhost:8000](http://localhost:8000))
* Esbuild in watch mode (listening on [localhost:8888](http://localhost:8888))

In a typical production environment you might want to deploy the frontend on a static webserver
like Apache or Caddy (recommended) and also use the webserver as a reverse-proxy in front of
the backend to handle logging, load-balancing, TLS termination and so on. In that case you only
need to run the backend process like so:

```sh
cd backend
poetry run ./main.py
```

Technology Choices
------------------

We try to keep things simple for this small application. Yet we need to glue together a
few things to make everything work.

### Backend

* Python - Programming Language
* Poetry - Package Management
* FastAPI - Web framework
* AutoGen - AI/LLM functionality

### Frontend

* Node.js - Runtime environment
* TypeScript - Type annotations for JavaScript
* Svelte - Component framework
* Esbuild - Bundler

Poetry Package Management
-------------------------

Python dependencies are managed with [Poetry](https://python-poetry.org/), which is similar in spirit
to NPM for Node.js developers. It handles installation and upgrades of all required external Python
packages, which for this reason need to be declared in the [backend/pyproject.toml](pyproject.toml) file,
plus it fully automates the usage of virtual environments. Here is a brief overview of the most important
commands. Run them from within the `backend` directory.

* `poetry init` - Start a new project with the Poetry package manager (already done of course 🙂)
* `poetry install` - Install all dependencies specified in [backend/pyproject.toml](pyproject.toml)
* `poetry add xyz` - Add another dependency to library `xyz`
* `poetry remove xyz` - Remove dependency to library `xyz` again
* `poetry show --tree` - Show all direct and indirect dependencies
* `poetry shell` - Start a new shell with the Python environment enabled
* `poetry run xyz` - Run console command `xyz` in the Python environment
* `poetry list` - Show all available sub-commands
* `poetry env use $(which python)` - Create new virtual Python environment
* `poetry env list` - List available environments
* `poetry env remove xyz` - Delete environment

NPM and esbuild
---------------

Of course everyone knows npm, at least when call yourself a web developer. If not, here is quick
rundown. The file [frontend/package.json](package.json) in the `frontend` directory declares the
frontend project, defining its dependencies and run-scripts for typical developer actions. It
allows you to run the following commands from within the `frontend` directory.

* `npm run build` - Build distribution files
* `npm run clean` - Delete distribution files
* `npm run watch` - Start watch mode for automatic rebuilds
* `npm run check` - Run all checks and tests: eslint, TypeScript, unit tests
* `npm run start` or `npm start` - Run from built distribution files
* `npm run tsc` - Check source code with TypeScript only

Testing the Websocket Communication
-----------------------------------

`npm run wscat` starts a command-line tool that automatically connects to the server.
Communication can be tested by manually typing in websocket messages, e.g.:

```json
{"code": "start_chat", "jwt": "", "body": {"language": "en"}}
```

```json
{"code": "user_chat_message", "jwt": "", "body": {"source": "user", "content": {"type": "speak", "speak": "Let's learn Python!"}}}
```

Building the Distribution Package
---------------------------------

First, commit and push all developments, because the build process will package the latest
HEAD from git – not the latest local changes!

Then run `npm run dist` from the root directory. This should rebuild everything and create
a new file in the `dist/` directory. This requires the `git` and `zip` command on your machine,
hence it is not 100% cross-platform compatible.

For the time being this file is then manually renamed and copied to https://wpvs.de/repo/elisa.