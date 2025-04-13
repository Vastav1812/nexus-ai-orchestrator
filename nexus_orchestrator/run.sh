#!/bin/bash

# Use Python 3.11 which has pip available
PYTHON_PATH="/usr/local/bin/python3.11"
if [ ! -x "$PYTHON_PATH" ]; then
  PYTHON_PATH="/Library/Frameworks/Python.framework/Versions/3.11/bin/python3"
fi

echo "Using Python at: $PYTHON_PATH"

# Create .env file from example if it doesn't exist
if [ ! -f .env ]; then
  echo "Creating .env file from .env.example..."
  cp .env.example .env
  echo "Please edit .env file to add your API keys before running the application"
fi

# Install required packages
echo "Installing required packages..."
$PYTHON_PATH -m pip install fastapi uvicorn python-dotenv httpx

# Run the simple orchestrator
echo "Starting AI Orchestrator..."
$PYTHON_PATH -m uvicorn simple_orchestrator:app --host 0.0.0.0 --port 8000 --reload

