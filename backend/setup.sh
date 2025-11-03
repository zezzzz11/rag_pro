#!/bin/bash

echo "Setting up RAG Pro Backend..."

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

echo "Backend setup complete!"
echo "To start the backend, run: ./start-backend.sh"
