FROM python:3-slim
MAINTAINER paper2code <contact@paper2code.com>

RUN apt-get update && \
    apt-get install -y \
    openssl \
    git

WORKDIR /opt/service
COPY requirements.txt .

RUN pip3 install --upgrade pip && \
    pip3 install -r requirements.txt

COPY main.py .
COPY data.py .

ENV LC_ALL=C.UTF-8 \
    LANG=C.UTF-8 \
    PYTHONDONTWRITEBYTECODE=1

ENTRYPOINT ["python3", "./main.py"]
