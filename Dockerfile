FROM ubuntu:18.04
MAINTAINER paper2code <contact@paper2code.com>

RUN apt-get update && \
    apt-get install -y sudo \
    build-essential \
    curl \
    libcurl4-openssl-dev \
    libssl-dev \
    wget \
    python3-dev \
    python3-pip \
    libxrender-dev \
    libxext6 \
    libsm6 \
    openssl

RUN mkdir -p /opt/service
COPY requirements.txt /opt/service
COPY server/main.py /opt/service/server.py
WORKDIR /opt/service

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3", "./server.py"]

