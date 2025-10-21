#!/bin/bash

# Privacy Data Deletion Tool - Database Setup Script for WSL
# This script helps you set up PostgreSQL on WSL

echo "=================================================="
echo "Privacy Data Deletion Tool - Database Setup (WSL)"
echo "=================================================="
echo ""

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "❌ PostgreSQL not found on WSL"
    echo ""
    echo "To install PostgreSQL on WSL, run:"
    echo "  sudo apt update"
    echo "  sudo apt install postgresql postgresql-contrib"
    echo ""
    exit 1
fi

echo "✓ PostgreSQL found"
echo ""

# Check if PostgreSQL service is running
if sudo service postgresql status | grep -q "online"; then
    echo "✓ PostgreSQL service is running"
else
    echo "⚠ PostgreSQL service not running. Starting..."
    sudo service postgresql start
    sleep 2

    if sudo service postgresql status | grep -q "online"; then
        echo "✓ PostgreSQL service started successfully"
    else
        echo "❌ Failed to start PostgreSQL service"
        exit 1
    fi
fi

echo ""
echo "=================================================="
echo "Next Steps:"
echo "=================================================="
echo ""
echo "1. Create .env file with your PostgreSQL credentials:"
echo "   cp .env.example .env"
echo "   nano .env"
echo ""
echo "2. Set your PostgreSQL password in .env:"
echo "   DB_PASSWORD=your_postgres_password"
echo ""
echo "   (Default PostgreSQL user is 'postgres')"
echo ""
echo "3. If you haven't set a password for PostgreSQL, do this:"
echo "   sudo -u postgres psql"
echo "   postgres=# ALTER USER postgres PASSWORD 'your_new_password';"
echo "   postgres=# \\q"
echo ""
echo "4. Initialize the database:"
echo "   source venv/bin/activate"
echo "   python src/database.py"
echo ""
echo "=================================================="
echo "PostgreSQL Status: READY"
echo "=================================================="
