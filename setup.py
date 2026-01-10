from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = ""
if readme_file.exists():
    long_description = readme_file.read_text(encoding="utf-8")

setup(
    name="orc-cli",
    version="1.0.0",
    packages=find_packages(include=['orc', 'orc.*']),
    include_package_data=True,
    # Dependencies and entry points are in pyproject.toml
    entry_points={
        'console_scripts': [
            'orc=orc.cli_main:main',
        ],
    },
    author="ORC Team",
    author_email="dev@orc-project.dev",
    description="ORC - Optimization & Refactoring Catalyst - AI-Powered Codebase Intelligence",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xytricit/orc",
    python_requires='>=3.8',
)