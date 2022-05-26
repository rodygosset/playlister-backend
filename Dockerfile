# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM --platform=linux/amd64 python:3.9

WORKDIR /code

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Get requirements
COPY ./requirements.txt /code/requirements.txt

# Configuring PostgreSQL
COPY ./init_postgres.sh /code/init_postgres.sh
RUN /bin/bash /code/init_postgres.sh

# Install production dependencies.
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy local code to the container image.
COPY ./ /code/app

CMD sudo service postgresql start && /code/app/launch.sh

# EXPOSE 8000
# CMD uvicorn app.main:app --host 0.0.0.0 --port 8000

# BUILD IMAGE
# docker build -t playlister-app-backend .

# RUN IMAGE
# docker run -it --name playlister-app-backend -p 8000:8000 playlister-app-backend
