#!/usr/bin/env python3
"""
Privacy Data Deletion Tool - Launcher
Allows users to choose between CLI and Desktop GUI interfaces.
"""

import sys
import os
from pathlib import Path

print(f"--- LAUNCHER INFO ---")
print(f"Running from Python executable: {sys.executable}")
print(f"Sys prefix (environment path): {sys.prefix}")
print(f"--- END LAUNCHER INFO ---")

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_banner():
    """Print the application banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║         🔐 PRIVACY DATA DELETION TOOL                    ║
    ║                                                          ║
    ║         Automate Your GDPR/CCPA Rights                  ║
    ║         100% Local • Privacy-First • Open Source        ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_interface_options():
    """Print interface selection options."""
    print("\n    Choose Your Interface:\n")
    print("    [1] 🖥️  CLI Mode (Command Line Interface)")
    print("        • Text-based terminal interface")
    print("        • Lightweight and fast")
    print("        • Perfect for servers and automation\n")

    print("    [2] 🎨 Desktop App (Graphical User Interface)")
    print("        • Modern, user-friendly interface")
    print("        • Dark/Light theme support")
    print("        • Visual progress tracking\n")

    print("    [3] ℹ️  About This Tool\n")
    print("    [4] ❌ Exit\n")


def show_about():
    """Show information about the tool."""
    clear_screen()
    print_banner()
    print("\n" + "="*60)
    print("ABOUT THIS TOOL")
    print("="*60)
    print("""
This tool helps you exercise your data deletion rights under:
  • GDPR (General Data Protection Regulation) - Article 17
  • CCPA (California Consumer Privacy Act)
  • Other privacy regulations worldwide

Features:
  ✓ Automatic company discovery from your emails
  ✓ Privacy contact finder (web scraping)
  ✓ Automated deletion request emails
  ✓ Reply tracking and status updates
  ✓ 100% local - your data never leaves your machine
  ✓ PostgreSQL database for reliable storage
  ✓ Gmail API integration (OAuth 2.0)

Privacy & Security:
  • All data stored locally on your computer
  • OAuth tokens secured in OS keychain
  • Email scanning uses headers only (privacy-preserving)
  • No telemetry, no tracking, no external services

Open Source:
  • GitHub: https://github.com/yourusername/privacy-deletion-tool
  • License: MIT
  • Contributions welcome!

Technical Stack:
  • Python 3.11+
  • PostgreSQL database
  • Gmail API (Google Cloud)
  • CustomTkinter (GUI framework)
  • BeautifulSoup4 (web scraping)
    """)
    print("="*60)
    input("\nPress Enter to return to main menu...")


def launch_cli():
    """Launch the CLI interface."""
    clear_screen()
    print_banner()
    print("\n    Launching CLI Mode...\n")

    # Add current directory to Python path
    project_dir = Path(__file__).parent
    if str(project_dir) not in sys.path:
        sys.path.insert(0, str(project_dir))

    # Import and run the CLI
    try:
        # Import the main module
        import importlib.util
        spec = importlib.util.spec_from_file_location("main", project_dir / "main.py")
        main_module = importlib.util.module_from_spec(spec)

        # Execute the main module
        spec.loader.exec_module(main_module)

        # The main.py should start its own loop and won't return here
        # But if it does, we exit gracefully
        sys.exit(0)

    except ImportError as e:
        print(f"    ✗ Error: Could not load CLI module: {e}")
        print("    Please ensure all dependencies are installed.")
        input("\n    Press Enter to return to launcher...")
        return
    except Exception as e:
        print(f"    ✗ Error running CLI: {e}")
        import traceback
        traceback.print_exc()
        input("\n    Press Enter to return to launcher...")
        return


def launch_gui():
    """Launch the Desktop GUI interface."""
    clear_screen()
    print_banner()
    print("\n    Launching Desktop GUI...\n")

    # Check if CustomTkinter is installed
    try:
        import customtkinter
    except ImportError:
        print("    ✗ Error: CustomTkinter not installed!")
        print("\n    To use the Desktop GUI, please install required packages:")
        print("    $ source venv/bin/activate")
        print("    $ pip install customtkinter pillow")
        print("\n    Or use the startup script:")
        print("    $ ./start.sh")
        print("\n    Alternatively, use CLI mode (Option 1)")
        input("\n    Press Enter to return to launcher...")
        return

    # Add current directory to Python path
    project_dir = Path(__file__).parent
    if str(project_dir) not in sys.path:
        sys.path.insert(0, str(project_dir))

    # Import and run the GUI
    try:
        # Import the main_gui module
        import importlib.util
        spec = importlib.util.spec_from_file_location("main_gui", project_dir / "main_gui.py")
        gui_module = importlib.util.module_from_spec(spec)

        # Execute the main_gui module
        spec.loader.exec_module(gui_module)

        # The main_gui.py should start its own loop and won't return here
        # But if it does, we exit gracefully
        sys.exit(0)

    except Exception as e:
        print(f"    ✗ Error: Could not launch GUI: {e}")
        import traceback
        traceback.print_exc()
        input("\n    Press Enter to return to launcher...")
        return


def check_dependencies():
    """Check if core dependencies are installed."""
    missing_deps = []

    core_deps = [
        ('psycopg2', 'PostgreSQL driver'),
        ('google.auth', 'Google Auth'),
        ('keyring', 'Secure token storage'),
        ('requests', 'HTTP requests'),
        ('bs4', 'BeautifulSoup4'),
        ('dotenv', 'python-dotenv')
    ]

    for module, name in core_deps:
        try:
            __import__(module)
        except ImportError:
            missing_deps.append(name)

    return missing_deps


def show_dependency_error(missing_deps):
    """Show error message for missing dependencies."""
    clear_screen()
    print_banner()
    print("\n    ✗ MISSING DEPENDENCIES\n")
    print("    The following required packages are not installed:")
    for dep in missing_deps:
        print(f"      • {dep}")

    print("\n    To install all dependencies, run:")
    print("    $ pip install -r requirements.txt")
    print("\n    Or install them individually:")
    print("    $ pip install psycopg2-binary google-api-python-client keyring")
    print("    $ pip install requests beautifulsoup4 python-dotenv")

    input("\n    Press Enter to exit...")
    sys.exit(1)


def main():
    """Main launcher function."""
    # Check dependencies first
    missing_deps = check_dependencies()
    if missing_deps:
        show_dependency_error(missing_deps)

    while True:
        clear_screen()
        print_banner()
        print_interface_options()

        choice = input("    Enter your choice (1-4): ").strip()

        if choice == '1':
            launch_cli()
        elif choice == '2':
            launch_gui()
        elif choice == '3':
            show_about()
        elif choice == '4':
            clear_screen()
            print_banner()
            print("\n    Thank you for using Privacy Data Deletion Tool!")
            print("    Your privacy matters. 🔐\n")
            sys.exit(0)
        else:
            print("\n    ✗ Invalid choice. Please enter 1, 2, 3, or 4.")
            input("    Press Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        clear_screen()
        print("\n\n    Goodbye! 👋\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n    ✗ Unexpected error: {e}")
        input("    Press Enter to exit...")
        sys.exit(1)
