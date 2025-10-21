#!/usr/bin/env python3
"""
Simple launcher that automatically uses the virtual environment Python.
This script detects if it's running in venv and re-executes itself if needed.
"""

import sys
import os
from pathlib import Path
import subprocess


def is_venv():
    """Check if we're running inside a virtual environment."""
    return (hasattr(sys, 'real_prefix') or
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))


def get_venv_python():
    """Get the path to the virtual environment's Python executable."""
    project_dir = Path(__file__).parent
    venv_dir = project_dir / 'venv'

    if os.name == 'nt':  # Windows
        python_path = venv_dir / 'Scripts' / 'python.exe'
    else:  # Unix/Linux/Mac
        python_path = venv_dir / 'bin' / 'python'

    return python_path if python_path.exists() else None


def main():
    """Main entry point."""

    # If we're NOT in a venv, try to re-execute with venv Python
    if not is_venv():
        venv_python = get_venv_python()

        if venv_python:
            print("Activating virtual environment automatically...")
            print()

            # Re-execute this script with venv Python
            launcher_path = Path(__file__).parent / 'launcher.py'
            result = subprocess.run([str(venv_python), str(launcher_path)])
            sys.exit(result.returncode)
        else:
            print("ERROR: Virtual environment not found!")
            print()
            print("Please create a virtual environment first:")
            print("  $ python3 -m venv venv")
            print("  $ source venv/bin/activate")
            print("  $ pip install -r requirements.txt")
            print()
            print("Or run the setup:")
            print("  $ ./start.sh")
            sys.exit(1)

    # If we ARE in a venv, just run the launcher
    project_dir = Path(__file__).parent
    launcher_path = project_dir / 'launcher.py'

    # Add project directory to path
    sys.path.insert(0, str(project_dir))

    # Execute the launcher
    with open(launcher_path) as f:
        code = compile(f.read(), launcher_path, 'exec')
        exec(code)


if __name__ == "__main__":
    main()
