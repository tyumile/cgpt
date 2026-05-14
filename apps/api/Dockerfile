FROM python:3.12-slim

WORKDIR /workspace/apps/api

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates gnupg npm \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g @openai/codex

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY . /workspace/apps/api
