"""Setup script for declarative-agent-sdk.

This file is maintained for backward compatibility.
The primary configuration is in pyproject.toml.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the version from sdk/__version__.py
version_file = Path(__file__).parent / "sdk" / "__version__.py"
version_info = {}
if version_file.exists():
    with open(version_file, "r") as f:
        exec(f.read(), version_info)
else:
    version_info = {"__version__": "0.1.0"}

# Read the long description from SDK_README.md
readme_file = Path(__file__).parent / "SDK_README.md"
long_description = ""
if readme_file.exists():
    with open(readme_file, "r", encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="declarative-agent-sdk",
    version=version_info["__version__"],
    description="A declarative SDK for creating Google ADK agents with YAML-based configuration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Organization",
    author_email="contact@example.com",
    url="https://github.com/yourusername/declarative-agent-sdk",
    packages=find_packages(where=".", include=["sdk", "sdk.*"]),
    python_requires=">=3.9",
    install_requires=[
        "google-adk>=0.1.0",
        "google-genai>=0.1.0",
        "pydantic>=2.0.0",
        "pyyaml>=6.0",
        "langgraph>=0.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
            "ruff>=0.1.0",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="google adk agents declarative yaml llm langgraph",
    license="MIT",
)
