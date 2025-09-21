#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

PORT="${PORT:-8080}"
HOST="${HOST:-0.0.0.0}"

echo "Starting Graphiti MCP Server (SSE) on ${HOST}:${PORT}"

# Use uv if available, otherwise fall back to python
if command -v uv >/dev/null 2>&1; then
  exec uv run uvicorn app:app --host "${HOST}" --port "${PORT}"
else
  # Fallback to regular python/pip
  python -m pip install --upgrade uvicorn fastapi
  exec python -m uvicorn app:app --host "${HOST}" --port "${PORT}"
fi
