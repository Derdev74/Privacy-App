#!/bin/bash

# Test script for WSL OAuth authentication

echo "=================================================="
echo "WSL OAuth Authentication Test"
echo "=================================================="
echo ""
echo "This will test Gmail authentication in WSL."
echo "You'll need to copy/paste a URL in your Windows browser."
echo ""
echo "Press Enter to continue, or Ctrl+C to cancel..."
read

# Activate virtual environment
source venv/bin/activate

# Run the authentication test
python src/gmail_auth.py

echo ""
echo "=================================================="
echo "Test Complete!"
echo "=================================================="
