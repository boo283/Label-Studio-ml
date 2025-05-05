FROM python:3.10.4-slim
# Set the working directory
WORKDIR /app

COPY minio_client_importer.py /app/minio_client_importer.py

ENV MINIO_ENDPOINT=localhost:9000

ENV MINIO_ROOT_USER=minio

ENV MINIO_ROOT_PASSWORD=minio123

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3-pip \
    && pip install --no-cache-dir \
    minio \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

CMD ["python", "/app/minio_client_importer.py"]