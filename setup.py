"""
Multi-Agent AI Tour Guide System
Setup configuration for package installation
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip()
        for line in requirements_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="multi-agent-tour-guide",
    version="1.0.0",
    author="Tour Guide Development Team",
    author_email="dev@tourguide.example.com",
    description="Intelligent multi-agent system that enriches navigation routes with contextual multimedia content",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/multi-agent-tour-guide",
    packages=find_packages(exclude=["tests*", "docs*", ".claude*"]),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=6.0.0",
            "sphinx-rtd-theme>=1.2.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "tour-guide=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "src": ["*.json", "*.yaml"],
    },
    project_urls={
        "Bug Reports": "https://github.com/yourusername/multi-agent-tour-guide/issues",
        "Source": "https://github.com/yourusername/multi-agent-tour-guide",
    },
    keywords="multi-agent ai tour-guide navigation google-maps youtube spotify claude-code",
    zip_safe=False,
)
