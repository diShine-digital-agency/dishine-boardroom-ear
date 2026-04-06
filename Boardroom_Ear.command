#!/bin/bash
# --------------------------------------------------
# diShine Boardroom Ear - Quick Launch
# --------------------------------------------------

# Ensure we are in the correct directory
cd "$(dirname "$0")"

# Check for venv
if [ ! -d "venv" ]; then
    echo "Virtual Environment (venv) not found. Running setup..."
    ./setup.sh
fi

# Activate venv
source venv/bin/activate

# Launch
python3 Boardroom_Ear.py

# Keep terminal open if it fails/ends
read -p "Press enter to exit..."
