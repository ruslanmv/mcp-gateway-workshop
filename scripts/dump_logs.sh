#!/usr/bin/env bash
set -euo pipefail
docker compose logs gateway | tee gateway.log
docker compose logs adapter | tee adapter.log
