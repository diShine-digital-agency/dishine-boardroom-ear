#!/bin/bash

# diShine Boardroom Ear - Setup Script
# This script sets up the virtual environment and installs all dependencies.

echo "--------------------------------------------------"
echo "   diShine Boardroom Ear - Initializing..."
echo "--------------------------------------------------"

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install it first."
    exit 1
fi

# Check for brew/ffmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "Warning: ffmpeg not found. It is required for processing audio."
    echo "Attempting to install via Homebrew..."
    if command -v brew &> /dev/null; then
        brew install ffmpeg
    else
        echo "Error: Homebrew not found. Please install ffmpeg manually: https://ffmpeg.org/download.html"
    fi
fi

# Create virtual environment
echo "Creating Virtual Environment (venv)..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
echo "Installing Python dependencies..."
pip install faster-whisper anthropic rich python-dotenv pydub PyYAML

# Download model (defaulting to small for high-speed setup)
echo "--------------------------------------------------"
echo "Setup Complete! "
echo "To start, use: ./Boardroom_Ear.command"
echo "--------------------------------------------------"
