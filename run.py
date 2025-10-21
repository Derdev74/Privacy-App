#!/usr/bin/env python3
"""
Simple launcher that automatically uses the virtual environment Python.
This script detects if it's running in venv and re-executes itself if needed,
then launches launcher.py using the correct interpreter.
"""

import sys
import os
from pathlib import Path
import subprocess

# Define project directory early
project_dir = Path(__file__).parent

def is_venv():
    """Check if we're running inside a virtual environment."""
    # Check for standard venv attributes
    return (hasattr(sys, 'real_prefix') or
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix))

def get_venv_python():
    """Get the path to the virtual environment's Python executable."""
    venv_dir = project_dir / 'venv'

    if os.name == 'nt':  # Windows
        # Standard location for python.exe in Windows venv
        python_path = venv_dir / 'Scripts' / 'python.exe'
    else:  # Unix/Linux/Mac (WSL falls here)
        # Use the name of the *current* python interpreter to find the venv one
        # (e.g., if you run 'python3 run.py', it looks for 'venv/bin/python3')
        python_exe_name = Path(sys.executable).name
        python_path = venv_dir / 'bin' / python_exe_name

    return python_path if python_path.exists() else None

def main():
    """Main entry point."""

    # --- Step 1: Ensure we are running inside the venv ---
    if not is_venv():
        venv_python = get_venv_python()

        if venv_python:
            print("Activating virtual environment automatically...")
            print()

            # Re-execute THIS script (run.py) using the venv's Python
            # This ensures the rest of the script runs within the venv context
            script_path = Path(__file__).resolve()
            try:
                # check=True will raise an error if the subprocess fails
                result = subprocess.run([str(venv_python), str(script_path)], check=True)
                # If subprocess runs successfully, exit the original script
                sys.exit(result.returncode)
            except subprocess.CalledProcessError as e:
                print(f"ERROR: Failed to re-execute script in virtual environment.")
                print(f"Command failed: {' '.join(e.cmd)}")
                print(f"Return code: {e.returncode}")
                if e.stderr:
                    print(f"Error output:\n{e.stderr.decode()}")
                sys.exit(e.returncode)
            except Exception as e:
                 print(f"ERROR: An unexpected error occurred while re-executing: {e}")
                 sys.exit(1)

        else:
            # Could not find the venv Python executable
            print("ERROR: Virtual environment Python executable not found!")
            # Try to determine the expected path for better error message
            venv_dir = project_dir / 'venv'
            python_exe_name = Path(sys.executable).name if sys.executable else 'python'
            expected_path = venv_dir / 'bin' / python_exe_name if os.name != 'nt' else venv_dir / 'Scripts' / 'python.exe'
            print(f"Looked for: {expected_path}")
            print()
            print("Please ensure the virtual environment exists and was created correctly.")
            print("Try creating/recreating it:")
            python_cmd = Path(sys.executable).name if sys.executable else 'python3' # Use current python command name
            print(f"  $ {python_cmd} -m venv venv")
            print("  $ source venv/bin/activate")
            print("  $ pip install -r requirements.txt")
            print()
            sys.exit(1)

    # --- Step 2: If we reach here, we ARE running inside the venv ---
    # print("Virtual environment is active.") # Optional: uncomment for confirmation

    # --- Step 3: Execute launcher.py using the current (venv) Python ---
    launcher_path = project_dir / 'launcher.py'

    if not launcher_path.exists():
        print(f"ERROR: launcher.py not found at {launcher_path}")
        sys.exit(1)

    # print("Executing launcher.py...") # Optional: uncomment for confirmation
    try:
        # sys.executable is guaranteed to be the venv python interpreter now
        # Use check=True to raise errors if launcher.py fails
        result = subprocess.run([sys.executable, str(launcher_path)], check=True)
        # Exit with the same code as launcher.py
        sys.exit(result.returncode)
    except subprocess.CalledProcessError as e:
        # Error happened inside launcher.py
        print(f"ERROR: launcher.py exited with an error.")
        # Error messages from launcher.py should have already been printed to stderr
        sys.exit(e.returncode)
    except Exception as e:
        print(f"ERROR: An unexpected error occurred while running launcher.py: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()