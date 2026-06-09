#!/bin/bash
uvicorn app.main:app --host 0.0.0.0 --port 9020 --reload --workers ${UVICORN_WORKERS:=1}