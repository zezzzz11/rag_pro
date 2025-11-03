#!/bin/bash
set -e

echo "Starting Ollama server..."
/bin/ollama serve &
OLLAMA_PID=$!

echo "Waiting for Ollama server to be ready..."
sleep 5

# Get model from environment variable or use default
MODEL=${OLLAMA_MODEL:-qwen2.5:0.5b}

echo "Pulling model: $MODEL"
/bin/ollama pull $MODEL

echo "Model $MODEL is ready!"
echo "Available models:"
/bin/ollama list

# Keep the server running
wait $OLLAMA_PID
