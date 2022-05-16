
# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.9-slim


WORKDIR /code

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Get requirements
COPY ./requirements.txt /code/requirements.txt

# Install production dependencies.
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy local code to the container image.
COPY ./ /code/app

EXPOSE 80

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]


# BUILD IMAGE
# docker build -t playlister-app-backend .

# RUN IMAGE
# docker run -it --name playlister-app-backend -p 8000:80 playlister-app-backend 
