#!/bin/bash
gunicorn app.main:app --bind 0.0.0.0:9020 --workers ${UVICORN_WORKERS:=1} --worker-class uvicorn.workers.UvicornWorker --log-level debug --timeout 60 --reload