"""Setup script for Stock Price Alerts."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text() if (this_directory / "README.md").exists() else ""

setup(
    name="stock-price-alerts",
    version="2.0.0",
    description="A comprehensive stock monitoring and alerting system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Stock Alerts Team",
    python_requires=">=3.8",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "requests>=2.31.0",
        "twilio>=8.10.0",
        "python-dotenv>=1.0.0",
        "PyYAML>=6.0.1",
        "click>=8.1.7",
        "rich>=13.7.0",
        "schedule>=1.2.1",
        "pandas>=2.1.4",
        "pytz>=2023.3",
        "secure-smtplib>=0.1.1",
        "colorlog>=6.8.0",
        "sqlalchemy>=2.0.23",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "stock-alerts=stock_alerts.cli:cli",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business :: Financial :: Investment",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
