#!/bin/bash

echo "Starting RAG Pro Backend..."

# Activate virtual environment
source venv/bin/activate

# Start server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
