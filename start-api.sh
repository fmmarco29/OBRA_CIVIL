#!/bin/bash
mkdir -p src/data
export PORT=${PORT:-10000}
uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
