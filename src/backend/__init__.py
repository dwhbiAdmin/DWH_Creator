"""
Backend Package - Core Business Logic
=====================================

This package contains the main business logic modules for the DWH Creator application.
Each module follows the specification's modular design principles with clear naming
conventions for logical flow.

Modules:
- A_project_manager: Project creation and management (step 1)  
- B_workbench_manager: Excel workbook operations (stages, artifacts, columns) (step 2)
- template_engine: Template processing and substitution (step 3)
- C_artifact_generator_manager: Final artifact creation and file generation (step 4)
- list_generator: List generation for template substitution (helper A)
- Z_git_manager: Git integration and version control (helper B)
- Y_ai_manager: AI-powered workbench assistance (helper C)
"""

from .A_project_manager import ProjectManager
from .B_workbench_manager import WorkbenchManager
from .template_engine import TemplateEngine
from .C_artifact_generator_manager import ArtifactGenerator
from .list_generator import ListGenerator
from .Z_git_manager import GitManager

__all__ = [
    "ProjectManager",
    "WorkbenchManager", 
    "TemplateEngine",
    "ArtifactGenerator",
    "ListGenerator",
    "GitManager"
]
