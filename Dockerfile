FROM ubuntu:18.04

# Prerequisites
RUN \
  apt-get update && \
  apt-get -y upgrade && \
  apt-get install -y python python-pip python-dev
  
RUN python -m pip install --upgrade pip


WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt
RUN ./send_out.sh
