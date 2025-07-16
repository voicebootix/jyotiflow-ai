"""
JyotiFlow.ai Backend Package
Spiritual guidance and astrology platform backend services
"""

__version__ = "1.0.0"
__author__ = "JyotiFlow.ai Team"

# Core modules
from . import deps
from . import db
from . import main

# Configuration
from . import config

# Authentication and security  
from . import auth

# Data models
from . import models

# Database utilities
from . import core_foundation_enhanced
from . import unified_startup_system

# Self-healing system
from . import database_self_healing_system
from . import startup_database_validator

__all__ = [
    "deps",
    "db", 
    "main",
    "config",
    "auth",
    "models",
    "core_foundation_enhanced",
    "unified_startup_system", 
    "database_self_healing_system",
    "startup_database_validator"
] 