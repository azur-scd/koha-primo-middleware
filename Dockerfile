# syntax=docker/dockerfile:1
FROM python:3.10.8-slim-buster
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . .
VOLUME ["/app"]
EXPOSE 5000
CMD [ "gunicorn", "--certfile=ssl/api-scd.univ-cotedazur.fr4529541.crt", "--keyfile=ssl/api-scd.univ-cotedazur.fr4529541.key", "--bind=0.0.0.0:5000", "wsgi:app"]

#docker build -t azurscd/koha-primo-middleware:latest .
#docker run -d --name koha-primo-middleware -p 5002:5000 -v C:/Users/geoffroy/Documents/GitHub/koha-primo-middleware:/app azurscd/koha-primo-middleware:latest