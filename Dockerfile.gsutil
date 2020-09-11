FROM            alpine:3.12
MAINTAINER     paper2code <contact@paper2code.com>

ARG             VERSION=4.9
RUN             apk add --no-cache --virtual .build-deps \
                    curl && \
                curl -sL https://storage.googleapis.com/pub/gsutil_$VERSION.tar.gz | tar xz && \
                find /gsutil -type f -name "*.pyc" -delete && \
                find /gsutil -type f -name "*.pyo" -delete && \
                find /gsutil -type d -name "__pycache__" -delete && \
                mv gsutil/* /usr/local/bin && \
                chmod +x /usr/local/bin/gsutil && \
                apk add --no-cache --virtual .run-deps \
                    python \
                    py-crcmod \
                    ca-certificates && \
                apk del .build-deps

RUN gsutil ls gs://arxiv-dataset/arxiv/metadata-v5

WORKDIR /opt/data
VOLUME /opt/data

ENTRYPOINT ["gsutil"]
CMD ["cp", "gs://arxiv-dataset/metadata-v5/arxiv-metadata-oai.json"]

# gs://arxiv-dataset/metadata-v5/arxiv-metadata-oai.json
# gs://arxiv-dataset/metadata-v5/authors-parsed.json
# gs://arxiv-dataset/metadata-v5/internal-citations.json
