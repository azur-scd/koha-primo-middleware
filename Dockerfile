# syntax=docker/dockerfile:1
FROM python:3.10.8-slim-buster
RUN apt-get update \ 
    && apt-get install -y locales locales-all
ENV LC_ALL fr_FR.UTF-8
ENV LANG fr_FR.UTF-8
ENV LANGUAGE fr_FR.UTF-8
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
COPY . .
VOLUME ["/app"]
EXPOSE 5000
CMD [ "gunicorn", "--certfile=ssl/localhost.crt", "--keyfile=ssl/localhost.key", "--bind=0.0.0.0:5000", "wsgi:app"]

#docker build -t azurscd/koha-primo-middleware:latest .
#docker run -d --name koha-primo-middleware -p 5002:5000 -v C:/Users/geoffroy/Documents/GitHub/koha-primo-middleware:/app azurscd/koha-primo-middleware:latest