"""
Backend Package - Core Business Logic
=====================================

This package contains the main business logic modules for the DWH Creator application.
Each module follows the logical letter-prefix naming convention aligned with menu structure.

Modules:
- a_project_manager: Project creation and management (Menu 1 & 2)  
- c_workbench_manager: Excel workbook operations (Menu 3)
- d_artifact_manager: Final artifact creation and file generation (Menu 4)
- e_documentation_manager: Documentation generation (Menu 5)
- z_ai_integration_manager: AI-powered workbench assistance (Shared utility)
"""

from .A_project_manager import ProjectManager
from .c_workbench_manager import WorkbenchManager
from .d_artifact_manager import ArtifactGenerator
from .e_documentation_manager import GitManager
from .z_ai_integration_manager import AIWorkbenchManager

__all__ = [
    "ProjectManager",
    "WorkbenchManager", 
    "ArtifactGenerator",
    "GitManager",
    "AIWorkbenchManager"
]
