from setuptools import setup, find_packages
import os

setup(
    name="orc-cli",
    version="1.0.0",
    packages=find_packages(include=['orc', 'orc.*']),
    py_modules=['run_orc'],  # Explicitly include the run_orc module
    entry_points={
        'console_scripts': [
            'orc=run_orc:main',
        ],
    },
    install_requires=[
        'click>=8.0.0',
        'rich>=10.0.0',
        'networkx>=2.6.0',
        'pyyaml>=5.4.0',
        'flask>=2.0.0',
        # Removed groq temporarily to see if that's causing issues
    ],
    author="ORC Team",
    description="Optimization & Refactoring Catalyst CLI",
    python_requires='>=3.6',
)