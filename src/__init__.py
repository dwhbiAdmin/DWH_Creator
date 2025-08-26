"""
DWH Creator - Data Warehouse Creation Tool
==========================================

A modular Python application for designing and generating data warehouse artifacts
including DDL scripts, ETL pipelines, and documentation.

Main Features:
- Metadata-driven design using Excel workbooks
- Template-based artifact generation
- Git integration for version control
- Modular architecture with clear separation of concerns

Architecture:
- Backend: Core business logic and data management
- Frontend: User interface (console, forms, future web)
- Utils: Common utilities and helpers
- Templates: DDL/ETL template files

Author: bezas.a@dwh-bi.com
"""

__version__ = "1.0.0"
__author__ = "bezas.a@dwh-bi.com"

# Core modules
from .backend import *
from .utils import *

__all__ = [
    "ProjectManager",
    "WorkbenchManager", 
    "ArtifactGenerator",
    "TemplateEngine",
    "ListGenerator",
    "GitManager",
    "ConfigManager",
    "Logger"
]
