FROM python:3.7-buster

RUN apt-get update && \
    apt-get -y install nano && \
    apt-get -y install similarity-tester && \
    pip install --upgrade pip && \
    pip install pipenv

COPY ./src/Pipfile ./src/Pipfile.lock /tmp/
RUN cd /tmp && pipenv install --deploy --dev --system
