"""
Setup script for Supply Chain Data Assistant package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="supply-chain-data-assistant",
    version="1.0.0",
    author="Supply Chain Data Assistant Contributors",
    description="A natural language to SQL converter for Databricks Unity Catalog tables",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alvinjchua888/supplychaindataassistant",
    py_modules=["data_assistant"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Database :: Database Engines/Servers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "openai>=1.0.0",
        "google-generativeai>=0.3.0",
        "python-dotenv>=1.0.0",
        "databricks-sql-connector>=2.0.0",
        "pydantic>=2.0.0",
        "typing-extensions>=4.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "supply-chain-assistant=data_assistant:main",
        ],
    },
)
