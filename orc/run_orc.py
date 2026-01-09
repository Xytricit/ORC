#!/usr/bin/env python
"""
Script to run the ORC CLI

Usage:
    orc              - Start AI chat interface (default)
    orc chat         - Start AI chat interface
    orc index <path> - Index a codebase
    orc analyse      - Run analysis
    orc <command>    - Other commands (dead, complexity, query, etc.)
"""
import sys
import os
from pathlib import Path

# Load environment variables from .env file
def load_env():
    """Load .env file from orc directory or current directory"""
    try:
        from dotenv import load_dotenv
        
        # Try multiple locations for .env
        possible_paths = [
            Path(__file__).parent / '.env',  # orc/.env (where run_orc.py is)
            Path.cwd() / '.env',              # current dir/.env
            Path.cwd() / 'orc' / '.env',      # current dir/orc/.env
        ]
        
        for env_path in possible_paths:
            if env_path.exists():
                load_dotenv(env_path, override=True)
                return  # Successfully loaded
    except ImportError:
        pass  # python-dotenv not installed, rely on system env vars

load_env()

# Add the orc directory to Python path so we can import orc_package
orc_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'orc')
sys.path.insert(0, orc_dir)

# Set console encoding to UTF-8 to handle Unicode characters
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


def main():
    """Main entry point for ORC CLI
    
    - 'orc' with no args starts AI chat
    - 'orc <command>' runs that command (analyse, index, dead, etc.)
    """
    from orc_package.cli.commands import cli
    cli()


if __name__ == '__main__':
    main()