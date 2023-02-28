#!/usr/bin/env bash

SCRIPT_DIR="$(dirname "$(realpath "${BASH_SOURCE[0]}")")"

docker run -d --name postgres -e POSTGRES_PASSWORD=max123 -p 5432:5432 -v "${SCRIPT_DIR}/init-db.sh":/docker-entrypoint-initdb.d/init-db.sh postgres
