#!/usr/bin/env python3
"""
ORC (Optimization & Refactoring Catalyst) CLI Application
This is the main entry point that assembles all CLI components
"""
import sys
import os

# Add both the project root and the orc directory to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'orc'))

def main():
    """Main entry point for the ORC CLI application"""
    try:
        # Import the CLI from the package structure
        from orc.orc_package.cli.commands import cli
        cli(prog_name="orc")  # Pass the program name explicitly
    except KeyboardInterrupt:
        print("\n\nSession interrupted by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()