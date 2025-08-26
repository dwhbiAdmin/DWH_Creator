"""
Backend Package - Core Business Logic
=====================================

This package contains the main business logic modules for the DWH Creator application.
Each module follows the specification's modular design principles with clear naming
conventions for logical flow.

Modules:
- project_manager: Project creation and management (step 1)
- workbench_manager: Excel workbook operations (stages, artifacts, columns) (step 2)
- template_engine: Template processing and substitution (step 3)
- artifact_generator: Final artifact creation and file generation (step 4)
- list_generator: List generation for template substitution (helper A)
- git_manager: Git integration and version control (helper B)
"""

from .project_manager import ProjectManager
from .workbench_manager import WorkbenchManager
from .template_engine import TemplateEngine
from .artifact_generator import ArtifactGenerator
from .list_generator import ListGenerator
from .git_manager import GitManager

__all__ = [
    "ProjectManager",
    "WorkbenchManager", 
    "TemplateEngine",
    "ArtifactGenerator",
    "ListGenerator",
    "GitManager"
]
