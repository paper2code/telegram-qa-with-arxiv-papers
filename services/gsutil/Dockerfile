FROM           python:3-slim
MAINTAINER     paper2code <contact@paper2code.com>

RUN             apt-get update && \
		echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
		apt-get install -y --no-install-recommends apt-transport-https ca-certificates gnupg curl gcc python3-dev python3-setuptools && \
		curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - && \
                apt-get update && \
		pip3 install --upgrade pip && \
		pip3 uninstall crcmod && \
		pip3 install --no-cache-dir -U crcmod && \
		apt-get install -y --no-install-recommends google-cloud-sdk

WORKDIR /opt/data
VOLUME /opt/data

ENTRYPOINT ["gsutil"]
