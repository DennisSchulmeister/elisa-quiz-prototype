Elisa: Learning Quizzes
=======================

1. [Description](#deployment)
1. [More Information](#more-information)
1. [Deployment](#deployment)
1. [Copyright](#copyright)

Description
===========

![Screenshot](screenshot.png)

”Hi, I am Elisa, your personal learning assistant“–A learning assistant that is able
to explain almost any topic and create quizzes to test your learning progress. It is
small, it is fun, it is engaging and easy to use. It is a chatbot backed by Large
Language Models or AI as most people would say. 🪄 And it is Free Software - as in
freedom and not in beer. 🍺

Right now it is an prototype and experiment that I did with students to build AI
learning tools. Actually it is not very fancy. But hopefully it is still useful and
given enough community interest many features could be added. Let's get in touch to
share ideas and get the stone rolling.

More Information
================

Everyone is gladly invited to build upon this, share it and enhance it. The following
documents provide some technical information.

 * [Developer Notes](./HACKING.md)
 * [Code of Conduct](./CODE_OF_CONDUCT.md)

Deployment
==========

**IMPORTANT:** Currently there is no user authentication whatsoever. If you plan to deploy
on a public server, you need to use the possibilities of your web server to restrict access,
if necessary.

This project consists of two parts:

* **Backend:** A simple python application built with [FastAPI](https://fastapi.tiangolo.com/).
* **Frontend:** A static Single Page App built with [Svelte](https://svelte.dev/)

Deployment usually means to start the backend server (by default using [Uvicorn](https://www.uvicorn.org/))
on a localhost network address (non-public) and configuring a web server to host the frontend
and act as a reverse-proxy for the backend. The only consideration is, that the web server must
also proxy web socket connections since frontend and backend communicate exclusively over web sockets
(to enable two-way message exchange in real-time). [Caddy](https://caddyserver.com/) is field proven
and super easy to setup (including automatic SSL certificate management!).

1. Get API key for your Large Language Model
1. Download the source code (e.g. with Git)
1. Install all dependencies (with `npm` and `poetry`)
1. Run the backend server (e.g. with the provided SystemD service file)
1. Setup frontend web server
1. Done!

Or use the provided Docker Compose setup for a plug-and-play solution. The following shell commands
show a manual setup on a typical Linux box (here Debian or Ubuntu). Please note, that you need to
have an API key for [OpenAI](https://platform.openai.com/) or any other
[LLM supported by LangChain](https://python.langchain.com/api_reference/langchain/chat_models/langchain.chat_models.base.init_chat_model.html)

```sh
# Install python runtime and poetry package manager (needed to run the backend)
sudo apt install python3 python3-poetry

# Install NodeJS and NPM package manager (only needed to build the frontend)
sudo apt install nodejs npm

# Download source code
# NOTE: When not installing to /opt/elisa-quiz please adopt paths in elisa-quiz.service
cd /opt
sudo git clone https://github.com/DennisSchulmeister/elisa-quiz.git

# Install all Node.js dependencies
sudo npm install

cd frontend
sudo npm install

# Build frontend (output will be in static/_bundle)
npm run build

# Create python environment and install python dependencies
cd ../backend
sudo poetry env use $(which python)
sudo poetry install

# Create .env file with OpenAI API key (or others supported by LangChain)
sudo cp .env.template .env
sudo nano .env

# Create and start SystemD service
cd ..
sudo cp elisa-quiz.service /etc/systemd/system
sudo systemctl enable elisa-quiz
sudo systemctl start elisa-quiz

# Check if the backend server has successfully started
sudo systemctl status elisa-quiz
sudo journalctl -fu elisa-quiz

# Install, enable and start webserver
sudo apt install caddy
sudo systemctl enable caddy
sudo systemctl start caddy

# Edit web server configuration (see example below)
sudo nano /etc/caddy/Caddyfile

# Reload web server configuration and test for errors
sudo systemctl reload caddy
sudo systemctl status caddy
sudo journalctl -fu caddy
```

Example Caddy configuration, assuming the backend server listens on `localhost:8000`.

```
your-domain.com {
    encode gzip
    file_server
    root * /opt/elisa-quiz/frontend/static/_bundle
    reverse_proxy /ws/* localhost:8000

    basic_auth {
        # Username "elisa", password "elisa"
        # See: https://caddyserver.com/docs/caddyfile/directives/basic_auth
        # Use "caddy hash-password" to create the password hash
		elisa $2a$14$39ezPLC8X9ODipWKGrVY/OEcNVULLLudQuUtEWxFNQUnaGyXZFNhK
    }
}
```

Yes, that's all. And Caddy even manages a [Let's Encrypt](https://letsencrypt.org/)
SSL certificate for us. As much as I loved [Apache](httpd.apache.org) (running it
for almost twenty yours on countless machines) – beat this!

If you need to start the backend server on another network address, edit the SystemD service
file and pass `--host <ip-address>` and/or `--port <port-number>` arguments to `main.py`.

Copyright
=========

**© 2025 DHBW Karlsruhe / Studiengang Wirtschaftsinformatik (Business Informatics)** <br>
**Dennis Schulmeister-Zimolong** <dennis@pingu-mail.de> <br/>
Licensed under the AGPL-3.0 license (Affero General Public License 3)