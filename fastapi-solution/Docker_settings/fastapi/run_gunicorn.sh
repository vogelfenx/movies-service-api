#!/bin/bash

#source /app/wait_db_up.sh

gunicorn -k uvicorn.workers.UvicornWorker --log-level info --bind 0.0.0.0:8000  src.main:app
