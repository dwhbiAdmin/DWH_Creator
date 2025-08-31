"""
Project Manager - Step 1
========================

Handles project creation and management operations.
Implements Tab A functionality from the specification.

Key responsibilities:
- New project creation with folder structure
- Opening existing projects
- Setting up default Excel workbook with proper sheets and headers
"""

import os
import subprocess
from pathlib import Path
from datetime import datetime

# Import utilities with proper path handling
import sys
current_dir = Path(__file__).parent
src_dir = current_dir.parent
sys.path.insert(0, str(src_dir))

from utils.config_manager import ConfigManager
from utils.file_utils import FileUtils
from utils.excel_utils import ExcelUtils
from utils.logger import Logger

class ProjectManager:
    """
    Manages DWH Creator projects including creation, opening, and basic setup.
    """
    
    def __init__(self):
        """Initialize the Project Manager."""
        self.config = ConfigManager()
        self.file_utils = FileUtils()
        self.excel_utils = ExcelUtils()
        self.logger = Logger()
        
    def get_default_projects_path(self) -> str:
        """
        Get the default projects directory path.
        
        Returns:
            str: Default projects directory path
        """
        # Get the DWH_Creator root directory (3 levels up from this file)
        current_file = Path(__file__)
        dwh_creator_root = current_file.parent.parent.parent
        return str(dwh_creator_root / "_DWH_Projects")
    
    def create_new_project(self, project_name: str, base_path: str = None) -> str:
        """
        Create a new DWH Creator project with folder structure and Excel workbook.
        
        Args:
            project_name: Name of the new project
            base_path: Base directory (defaults to _DWH_Projects)
            
        Returns:
            str: Path to the created project directory
        """
        try:
            # Determine base path
            if base_path is None:
                base_path = self.get_default_projects_path()
                
            # Create base directory if it doesn't exist
            os.makedirs(base_path, exist_ok=True)
            
            # Create project directory
            project_dir_name = f"Project_{project_name}"
            project_path = os.path.join(base_path, project_dir_name)
            
            if os.path.exists(project_path):
                raise Exception(f"Project directory already exists: {project_path}")
                
            os.makedirs(project_path)
            self.logger.info(f"Created project directory: {project_path}")
            
            # Create project subdirectories
            subdirs = self.config.get_default_subdirectories()
            for subdir in subdirs:
                subdir_path = os.path.join(project_path, subdir)
                os.makedirs(subdir_path, exist_ok=True)
                self.logger.info(f"Created subdirectory: {subdir}")
                
            # Create stage-specific artifact subdirectories
            artifacts_path = os.path.join(project_path, "4_artifacts")
            stage_dirs = ["1_bronze", "2_silver", "3_gold", "4_mart", "PBI", "9_archive"]
            for stage_dir in stage_dirs:
                stage_path = os.path.join(artifacts_path, stage_dir)
                os.makedirs(stage_path, exist_ok=True)
                # Create DDL and ETL subdirectories for bronze, silver, gold
                if stage_dir in ["1_bronze", "2_silver", "3_gold"]:
                    os.makedirs(os.path.join(stage_path, "DDLs"), exist_ok=True)
                    os.makedirs(os.path.join(stage_path, "ETLs"), exist_ok=True)
                # Create only DDLs for mart
                elif stage_dir == "4_mart":
                    os.makedirs(os.path.join(stage_path, "DDLs"), exist_ok=True)
                    
            # Create Excel workbook
            workbook_path = os.path.join(project_path, "2_workbench", f"workbench_{project_name}.xlsx")
            self._create_excel_workbook(workbook_path, project_name)
            
            self.logger.info(f"Project '{project_name}' created successfully at: {project_path}")
            return project_path
            
        except Exception as e:
            self.logger.error(f"Failed to create project: {str(e)}")
            raise
    
    def _create_excel_workbook(self, workbook_path: str, project_name: str):
        """
        Create the Excel workbook with the three main sheets and default data.
        
        Args:
            workbook_path: Path where to create the workbook
            project_name: Name of the project
        """
        # Get sheet configurations
        stages_config = self.config.get_stages_sheet_config()
        artifacts_config = self.config.get_artifacts_sheet_config()
        columns_config = self.config.get_columns_sheet_config()
        
        # Create workbook with all three sheets
        sheets_config = {
            'Stages': stages_config,
            'Artifacts': artifacts_config,
            'Columns': columns_config
        }
        
        if self.excel_utils.create_workbook_with_sheets(workbook_path, sheets_config):
            self.logger.info(f"Created Excel workbook: {workbook_path}")
        else:
            raise Exception(f"Failed to create Excel workbook: {workbook_path}")
    
    def open_existing_project(self, project_path: str) -> bool:
        """
        Open an existing DWH Creator project.
        
        Args:
            project_path: Path to existing project directory
            
        Returns:
            bool: True if project opened successfully
        """
        try:
            if not os.path.exists(project_path):
                self.logger.error(f"Project path does not exist: {project_path}")
                return False
                
            # Validate project structure
            if not self._validate_project_structure(project_path):
                self.logger.error(f"Invalid project structure: {project_path}")
                return False
                
            self.logger.info(f"Opened project: {project_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to open project: {str(e)}")
            return False
    
    def _validate_project_structure(self, project_path: str) -> bool:
        """
        Validate that the project has the expected structure.
        
        Args:
            project_path: Path to project directory
            
        Returns:
            bool: True if structure is valid
        """
        required_dirs = ["2_workbench", "4_artifacts"]
        
        for req_dir in required_dirs:
            dir_path = os.path.join(project_path, req_dir)
            if not os.path.exists(dir_path):
                return False
                
        # Check for workbook file
        workbench_dir = os.path.join(project_path, "2_workbench")
        xlsx_files = [f for f in os.listdir(workbench_dir) if f.endswith('.xlsx') and f.startswith('workbench_')]
        
        return len(xlsx_files) > 0
    
    def list_available_projects(self) -> list:
        """
        List all available projects in the default projects directory.
        
        Returns:
            list: List of project dictionaries with name and path
        """
        projects = []
        projects_dir = self.get_default_projects_path()
        
        if not os.path.exists(projects_dir):
            return projects
            
        for item in os.listdir(projects_dir):
            item_path = os.path.join(projects_dir, item)
            if os.path.isdir(item_path) and item.startswith("Project_"):
                if self._validate_project_structure(item_path):
                    project_name = item.replace("Project_", "")
                    projects.append({
                        'name': project_name,
                        'path': item_path
                    })
                    
        return projects
    
    def open_excel_workbook(self, project_path: str) -> bool:
        """
        Open the Excel workbook for the project.
        
        Args:
            project_path: Path to project directory
            
        Returns:
            bool: True if workbook opened successfully
        """
        try:
            workbench_dir = os.path.join(project_path, "2_workbench")
            xlsx_files = [f for f in os.listdir(workbench_dir) if f.endswith('.xlsx') and f.startswith('workbench_')]
            
            if not xlsx_files:
                self.logger.error("No workbook file found")
                return False
                
            workbook_path = os.path.join(workbench_dir, xlsx_files[0])
            
            # Open Excel file with default application
            if os.name == 'nt':  # Windows
                os.startfile(workbook_path)
            elif os.name == 'posix':  # macOS and Linux
                subprocess.call(['open', workbook_path])
                
            self.logger.info(f"Opened Excel workbook: {workbook_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to open Excel workbook: {str(e)}")
            return False
    
    def setup_git_integration(self, project_path: str, email: str) -> bool:
        """
        Setup GitHub integration for the project.
        
        Args:
            project_path: Path to project directory
            email: User email for Git configuration
            
        Returns:
            bool: True if Git setup successful
        """
        # TODO: Implement Git integration
        # This will be implemented when we work on the GitManager
        pass
