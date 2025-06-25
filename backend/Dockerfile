#===============================================================================
# Backend build container
#===============================================================================
FROM python:slim AS build

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV MSGPACK_PUREPYTHON 1

WORKDIR /app
COPY pyproject.toml .
COPY poetry.lock .

RUN python -m venv .env
RUN .env/bin/pip install poetry poetry-plugin-export
RUN .env/bin/poetry export --format=requirements.txt --output=requirements.txt

#===============================================================================
# Backend runtime container
#===============================================================================
FROM python:slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV MSGPACK_PUREPYTHON 1

WORKDIR /app

COPY --from=build /app/requirements.txt . 
RUN python -m venv .venv
RUN .venv/bin/pip install -r requirements.txt

COPY . .
CMD [".venv/bin/python", "main.py"]