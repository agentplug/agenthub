#!/usr/bin/env python3
"""
Setup script for AgentHub
This is a fallback setup script for environments that don't support pyproject.toml
"""

import os

from setuptools import find_packages, setup


# Read the README file
def read_readme():
    with open("README.md", encoding="utf-8") as fh:
        return fh.read()


# Read requirements
def read_requirements():
    with open("requirements.txt", encoding="utf-8") as fh:
        return [
            line.strip() for line in fh if line.strip() and not line.startswith("#")
        ]


# Check if requirements.txt exists
if os.path.exists("requirements.txt"):
    install_requires = read_requirements()
else:
    # Fallback to basic requirements
    install_requires = [
        "pyyaml>=6.0.1",
        "click>=8.1.7",
        "rich>=13.7.1",
        "pydantic>=2.11.0",
        "mcp[cli]>=1.13.1",
    ]

setup(
    name="agenthub",
    version="0.1.0",
    author="William",
    author_email="william@agenthub.dev",
    description="AgentHub - The App Store for AI Agents",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/agenthub/agenthub",
    project_urls={
        "Homepage": "https://github.com/agenthub/agenthub",
        "Documentation": "https://docs.agenthub.dev",
        "Repository": "https://github.com/agenthub/agenthub",
        "Issues": "https://github.com/agenthub/agenthub/issues",
        "Changelog": "https://github.com/agenthub/agenthub/blob/main/CHANGELOG.md",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries",
        "Topic :: System :: Systems Administration",
        "Typing :: Typed",
    ],
    python_requires=">=3.11",
    install_requires=install_requires,
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-cov>=4.0.0",
            "pytest-asyncio>=0.23.0",
            "pytest-mock>=3.14.0",
            "black>=24.0.0",
            "mypy>=1.8.0",
            "ruff>=0.2.0",
            "pre-commit>=3.6.0",
            "types-pyyaml>=6.0.12",
            "safety>=3.0.0",
            "coverage>=7.9.0",
        ],
        "rag": [
            "llama-index>=0.12.0",
            "chromadb>=1.0.0",
            "sentence-transformers>=5.0.0",
            "faiss-cpu>=1.11.0",
        ],
        "code": ["docker>=7.0.0"],
        "full": [
            "agenthub[dev,rag,code]",
        ],
    },
    entry_points={
        "console_scripts": [
            "agenthub=agenthub.cli.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
