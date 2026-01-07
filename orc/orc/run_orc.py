#!/usr/bin/env python
"""
Script to run the ORC CLI
"""
import sys
import os

# Add the parent directory to Python path so we can import orc_package
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Set console encoding to UTF-8 to handle Unicode characters
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

from orc_package.cli.commands import cli

if __name__ == '__main__':
    cli()