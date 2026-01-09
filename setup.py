from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = ""
if readme_file.exists():
    long_description = readme_file.read_text(encoding="utf-8")

setup(
    name="orc-cli",
    version="2.0.0",
    packages=find_packages(include=['orc', 'orc.*']),
    entry_points={
        'console_scripts': [
            'orc=orc.cli_main:main',
        ],
    },
    install_requires=[
        'click>=8.0.0',
        'rich>=10.0.0',
        'networkx>=2.6.0',
        'pyyaml>=5.4.0',
        'httpx>=0.24.0',
        'python-dotenv>=1.0.0',
        'dataclasses-json>=0.5.0',
        'prompt_toolkit>=3.0.0',
        # AI providers included by default
        'groq>=0.5.0',
        'openai>=1.0.0',
        'anthropic>=0.18.0',
        'google-generativeai>=0.4.0',
    ],
    extras_require={
        'ai': [
            'groq>=0.5.0',
            'openai>=1.0.0',
            'anthropic>=0.18.0',
            'google-generativeai>=0.4.0',
        ],
        'web': [
            'flask>=2.0.0',
            'flask-login>=0.6.2',
            'flask-sqlalchemy>=3.0.5',
            'flask-bcrypt>=1.0.1',
            'flask-wtf>=1.1.1',
            'wtforms>=3.0.1',
            'email-validator>=2.0.0',
            'gunicorn>=20.1.0',
        ],
        'api': [
            'fastapi>=0.100.0',
            'uvicorn>=0.23.0',
        ],
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'isort>=5.12.0',
        ],
        'all': [
            'groq>=0.5.0',
            'openai>=1.0.0',
            'anthropic>=0.18.0',
            'google-generativeai>=0.4.0',
            'flask>=2.0.0',
            'flask-login>=0.6.2',
            'flask-sqlalchemy>=3.0.5',
            'flask-bcrypt>=1.0.1',
            'flask-wtf>=1.1.1',
            'wtforms>=3.0.1',
            'email-validator>=2.0.0',
            'gunicorn>=20.1.0',
            'fastapi>=0.100.0',
            'uvicorn>=0.23.0',
        ],
    },
    author="ORC Team",
    author_email="dev@orc-project.dev",
    description="ORC - Optimization & Refactoring Catalyst - AI-Powered Codebase Intelligence",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xytricit/orc",
    project_urls={
        "Bug Tracker": "https://github.com/xytricit/orc/issues",
        "Documentation": "https://github.com/xytricit/orc/blob/main/README.md",
        "Source Code": "https://github.com/xytricit/orc",
        "Changelog": "https://github.com/xytricit/orc/blob/main/CHANGELOG.md",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Code Generators",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    keywords="code-analysis refactoring optimization ai codebase-intelligence static-analysis",
    python_requires='>=3.8',
    license="MIT",
    include_package_data=True,
)