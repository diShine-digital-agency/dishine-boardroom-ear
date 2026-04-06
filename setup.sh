#!/bin/bash
# --------------------------------------------------
# diShine Boardroom Ear — Setup Script
# Supports: macOS (Apple Silicon & Intel), Linux x64
# --------------------------------------------------

set -euo pipefail

BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
RESET="\033[0m"

info()    { echo -e "${BOLD}[INFO]${RESET} $*"; }
success() { echo -e "${GREEN}[OK]${RESET}   $*"; }
warn()    { echo -e "${YELLOW}[WARN]${RESET} $*"; }
error()   { echo -e "${RED}[ERR]${RESET}  $*"; exit 1; }

echo "--------------------------------------------------"
echo "   diShine Boardroom Ear — Initialising..."
echo "--------------------------------------------------"

# --- Python ---
if ! command -v python3 &>/dev/null; then
    error "Python 3 is not installed. Install it from https://python.org or via Homebrew: brew install python"
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || { [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 9 ]; }; then
    error "Python 3.9+ required (found $PYTHON_VERSION). Upgrade via Homebrew: brew upgrade python"
fi
success "Python $PYTHON_VERSION detected."

# --- FFmpeg ---
if ! command -v ffmpeg &>/dev/null; then
    warn "ffmpeg not found. Attempting to install..."
    if command -v brew &>/dev/null; then
        brew install ffmpeg
    elif command -v apt-get &>/dev/null; then
        sudo apt-get install -y ffmpeg
    else
        warn "Could not auto-install ffmpeg. Please install it manually: https://ffmpeg.org/download.html"
    fi
else
    success "ffmpeg detected."
fi

# --- Virtual environment ---
if [ ! -d "venv" ]; then
    info "Creating virtual environment..."
    python3 -m venv venv
fi
success "Virtual environment ready."

# Activate
# shellcheck source=/dev/null
source venv/bin/activate

# --- pip ---
info "Upgrading pip..."
pip install --upgrade pip --quiet

# --- Dependencies ---
info "Installing Python dependencies from requirements.txt..."
pip install -r requirements.txt --quiet
success "Dependencies installed."

# --- Directories ---
info "Creating required directories..."
mkdir -p drop_here transcripts
success "Directories ready: drop_here/ and transcripts/"

# --- .env ---
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    cp .env.example .env
    info ".env created from .env.example. Add your ANTHROPIC_API_KEY if you want Strategic Plans."
fi

# --- Config ---
if [ ! -f "config.yaml" ] && [ -f "tests/sample_config.yaml" ]; then
    cp tests/sample_config.yaml config.yaml
    info "config.yaml created from sample. Review and adjust model_size if needed."
fi

echo ""
echo "--------------------------------------------------"
echo -e "${GREEN}${BOLD}Setup complete!${RESET}"
echo ""
echo "  Start:       ./Boardroom_Ear.command"
echo "  Or:          python3 Boardroom_Ear.py --help"
echo "  Health check: python3 Boardroom_Ear.py --health-check"
echo "--------------------------------------------------"
