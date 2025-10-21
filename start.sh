#!/bin/bash
# Privacy Data Deletion Tool - Startup Script for WSL/Linux
# This script activates the virtual environment and launches the application

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "Privacy Data Deletion Tool"
echo "=========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "ERROR: Virtual environment not found!"
    echo "Please run: python3 -m venv venv"
    echo "Then: source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import customtkinter" 2>/dev/null; then
    echo "WARNING: Dependencies not fully installed."
    echo "Installing requirements..."
    pip install -r requirements.txt
fi

# Launch the application
echo "Launching Privacy Data Deletion Tool..."
echo ""

python launcher.py

# Deactivate when done
deactivate
