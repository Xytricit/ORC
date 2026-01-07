#!/usr/bin/env python
"""
Simple test code for ORC analysis
"""

def used_function():
    """This function is used"""
    print("I am used")
    return 42

def unused_function():
    """This function is never called"""
    print("I am unused")
    return 100

def another_unused_function():
    """Another unused function"""
    x = 1 + 1
    y = x * 2
    return y

# Only call the used function
if __name__ == "__main__":
    result = used_function()
    print(f"Result: {result}")