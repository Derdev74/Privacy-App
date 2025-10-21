@echo off
REM Privacy Data Deletion Tool - Startup Script for Windows
REM This script activates the virtual environment and launches the application

echo ==========================================
echo Privacy Data Deletion Tool
echo ==========================================
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv venv
    echo Then: venv\Scripts\activate ^&^& pip install -r requirements.txt
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if dependencies are installed
python -c "import customtkinter" 2>nul
if errorlevel 1 (
    echo WARNING: Dependencies not fully installed.
    echo Installing requirements...
    pip install -r requirements.txt
)

REM Launch the application
echo Launching Privacy Data Deletion Tool...
echo.

python launcher.py

REM Deactivate when done
call venv\Scripts\deactivate.bat

pause
