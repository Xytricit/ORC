#!/usr/bin/env python3
"""
Simple test to check if the banner and startup info work
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from orc.banner import get_orc_banner, print_startup_info

def test_basic():
    print("Testing basic functionality...")
    print(get_orc_banner())
    print(print_startup_info("my-webapp", 47392, ["Python", "JavaScript", "TypeScript"]))
    print("Basic functionality test completed.")

if __name__ == "__main__":
    test_basic()