# syntax=docker/dockerfile:1

FROM python:3.10-slim-buster AS builder

RUN apt-get update && apt-get install -y \
  gcc \
  git \
  libpq-dev \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

FROM python:3.10-slim-buster

RUN apt-get update && apt-get install -y \
  libpq5 \
  && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app /app
COPY --from=builder /usr/local /usr/local
COPY --from=builder /root/.cache /root/.cache

WORKDIR app

COPY bin/ingester .

ENTRYPOINT ["/app/ingester"]
