FROM nvidia/cuda:10.2-cudnn7-devel-ubuntu18.04
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
    nano \
    bash \
    git

RUN mkdir -p /opt/service
COPY requirements-service.txt /opt/service
COPY summarizer /opt/service/summarizer
COPY server.py /opt/service
WORKDIR /opt/service

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements-service.txt
RUN python3 -c 'import torch; print(torch.cuda.is_available())'

# CMD ["python3", "./server.py"]
ENTRYPOINT ["python3", "./server.py"]

