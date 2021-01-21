FROM python:3

RUN apt-get update && apt-get -y install gcc
RUN easy_install pip && pip install --upgrade pip

WORKDIR /pydriller_basics
COPY . /pydriller_basics

RUN pip install -r requirements.txt
