#!/bin/bash
gunicorn --bind 0:8000 app.main:app --reload -w ${GUNICORN_WORKERS:=1}