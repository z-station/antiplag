FROM python:3.12-bookworm

ENV POETRY_VERSION=2.1.3 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

RUN apt-get update && \
    apt-get -y install nano && \
    apt-get -y install similarity-tester && \
    pip install --upgrade pip "poetry==${POETRY_VERSION}"

COPY ./src/pyproject.toml ./src/poetry.lock /tmp/
RUN cd /tmp && \
    poetry config virtualenvs.create false && \
    poetry install --only main --no-root --no-ansi

WORKDIR /app/src
