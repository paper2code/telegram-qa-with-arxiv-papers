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
    openssl \
    git

WORKDIR /opt/service
COPY requirements.txt .

RUN pip3 install --upgrade pip && \
    pip3 install -r requirements.txt

COPY main.py server.py
COPY data.py data.py

ENTRYPOINT ["python3", "./server.py"]

