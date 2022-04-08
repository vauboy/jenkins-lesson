FROM python:3.8-slim-bullseye

WORKDIR /unittests

COPY . .

RUN pip3 install -r requirements.txt

