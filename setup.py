"""
Setup configuration for JyotiFlow.ai Backend Package
"""

from setuptools import setup, find_packages

setup(
    name="jyotiflow-backend",
    version="1.0.0",
    description="JyotiFlow.ai Backend - Spiritual guidance and astrology platform",
    author="JyotiFlow.ai Team",
    author_email="dev@jyotiflow.ai",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        # Core dependencies
        "fastapi>=0.68.0",
        "uvicorn[standard]>=0.15.0",
        "asyncpg>=0.24.0",
        "pydantic>=1.8.0",
        
        # Authentication & Security
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
        "python-multipart>=0.0.5",
        
        # OpenAI Integration
        "openai>=1.0.0",
        
        # Database & Migration
        "alembic>=1.7.0",
        "sqlalchemy>=1.4.0",
        
        # Monitoring & Logging
        "sentry-sdk[fastapi]>=1.5.0",
        
        # Utilities
        "python-dotenv>=0.19.0",
        "httpx>=0.24.0",
        "aiofiles>=0.7.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.2.0",
            "pytest-asyncio>=0.15.0",
            "black>=21.0.0",
            "flake8>=3.9.0",
            "mypy>=0.910",
        ],
        "test": [
            "pytest>=6.2.0",
            "pytest-asyncio>=0.15.0",
            "pytest-cov>=2.12.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "jyotiflow-server=backend.main:main",
            "jyotiflow-validate=backend.validate_self_healing:main",
            "jyotiflow-test=backend.test_self_healing_system:main",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)