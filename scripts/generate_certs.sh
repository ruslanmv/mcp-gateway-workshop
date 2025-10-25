#!/usr/bin/env bash
set -euo pipefail
mkdir -p certs
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout certs/key.pem -out certs/cert.pem -subj "/CN=localhost"
echo "Generated certs in ./certs"
