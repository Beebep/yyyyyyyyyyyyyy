FROM ubuntu:14.04

# Prerequisites
RUN \
  apt-get update && \
  apt-get -y upgrade && \
  apt-get install -y python python-pip python-dev


WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt
CMD ["python3", "./src/mlp.py"]
CMD ["send_out.sh"]
