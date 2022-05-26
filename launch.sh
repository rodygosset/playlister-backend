#!/bin/bash

# Visit https://docs.docker.com/config/containers/multi-service_container/ for more info about this file.

# turn on bash's job control
set -m

# Start uvicorn server and put it in the background
cd /code && uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Wait for for the uvicorn server to start, and populate the database
sleep 5 && python3 /code/app/scripts/db_populate.py

# now we bring uvicorn logs back into the foreground
# and leave it there
fg %1