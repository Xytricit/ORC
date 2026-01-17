"""
ORC - AI-Powered Codebase Intelligence Platform
Setup configuration for pip installation
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8') if (this_directory / "README.md").exists() else ""

setup(
    name='orc-codebase',
    version='1.0.0',
    author='ORC Team',
    author_email='',
    description='AI-powered codebase intelligence platform for analysis, optimization, and understanding',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/xytricit/orc',
    packages=find_packages(exclude=['tests', 'tests.*', 'archive', 'archive.*', 'component1_core_indexing']),
    python_requires='>=3.8',
    install_requires=[
        'click>=8.0.0',
        'pyyaml>=5.4.0',
        'networkx>=2.6.0',
        'pygments>=2.10.0',
        'prompt-toolkit>=3.0.0',
        'python-dotenv>=0.19.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=2.12.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'orc=orc.cli.cli_main:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Quality Assurance',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    keywords='code-analysis, ai, codebase-intelligence, static-analysis, optimization',
    project_urls={
        'Bug Reports': 'https://github.com/xytricit/orc/issues',
        'Source': 'https://github.com/xytricit/orc',
    },
)
