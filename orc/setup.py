from setuptools import setup, find_packages

setup(
    name="orc",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "click>=8.0.0",
        "rich>=10.0.0",
        "networkx>=2.6.0",
        "pyyaml>=5.4.0",
        "flask>=2.0.0",
        "dataclasses-json>=0.5"
    ],
    entry_points={
        "console_scripts": [
            "orc=orc.run_orc:cli"
        ]
    }
)