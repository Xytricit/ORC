from setuptools import setup, find_packages

setup(
    name="orc",
    version="2.0.0",
    description="ORC - Optimization & Refactoring Catalyst - AI-Powered Codebase Intelligence",
    packages=find_packages(),
    install_requires=[
        "click>=8.0.0",
        "rich>=10.0.0",
        "networkx>=2.6.0",
        "pyyaml>=5.4.0",
        "flask>=2.0.0",
        "dataclasses-json>=0.5",
        "groq>=0.5.0",
        "openai>=1.0.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "orc=run_orc:main"
        ]
    },
    python_requires=">=3.8",
)