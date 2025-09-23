"""
Workbench Manager - Step 2
==========================

Handles Excel workbook operations for stages, artifacts, and columns sheets.
Implements Tab B functionality from the specification.

Key responsibilities:
- Managing the three main sheets: Stages, Artifacts, Columns
- Import/Assign operations from source files
- AI comment generation for artifacts and columns
- Cascade operations for deterministic column filling
- Sync and validation operations
"""

# ANCHOR: Imports and Dependencies

import os
import subprocess
import pandas as pd
import glob
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# Import utilities with proper path handling
import sys
current_dir = Path(__file__).parent
src_dir = current_dir.parent
sys.path.insert(0, str(src_dir))

from utils.c_workbench_excel_utils import ExcelUtils
from utils.z_logger import Logger
from utils.c_workbench_config_utils import ConfigManager
from utils.c_workbench_cascade_utils import ColumnCascadingEngine
from utils.c_workbench_1_import_raw_utils import RawFileImporter
from .z_ai_integration_manager import AIWorkbenchManager

# ANCHOR: WorkbenchManager Class Definition

class WorkbenchManager:
    """
    Manages Excel workbook operations and sheet manipulations.
    """
    
    # ANCHOR: Initialization and Setup Methods
    def __init__(self, project_path: str = None, openai_api_key: str = None):
        """
        Initialize the Workbench Manager.
        
        Args:
            project_path: Path to the project directory
            openai_api_key: OpenAI API key for AI comment generation
        """
        self.project_path = project_path
        self.workbook_path = None
        self.excel_utils = ExcelUtils()
        self.logger = Logger()
        self.config = ConfigManager()
        self.openai_api_key = openai_api_key
        self.ai_workbench = None  # Will be initialized when workbook is found
        self.cascading_engine = None  # Will be initialized when workbook is found
        self.raw_file_importer = None  # Will be initialized when workbook is found
        
        if project_path:
            self._find_workbook()
    
    def _find_workbook(self):
        """Find the workbook file in the project."""
        if not self.project_path:
            return
            
        workbench_dir = os.path.join(self.project_path, "2_workbench")
        workbook_pattern = os.path.join(workbench_dir, "workbench_*.xlsx")
        workbooks = glob.glob(workbook_pattern)
        
        # Filter out temporary files and configuration files
        workbooks = [wb for wb in workbooks if not os.path.basename(wb).startswith("~$") and "configuration" not in os.path.basename(wb)]
        
        if workbooks:
            self.workbook_path = workbooks[0]
            self.logger.info(f"Found workbook: {self.workbook_path}")
            # Initialize AI workbench manager
            self.ai_workbench = AIWorkbenchManager(self.workbook_path, self.openai_api_key)
            # Initialize column cascading engine
            # Initialize cascading engine with workbench manager reference
            self.cascading_engine = ColumnCascadingEngine(self.workbook_path)
            self.cascading_engine.workbench_manager = self  # Pass reference for AI access
            # Initialize raw file importer
            self.raw_file_importer = RawFileImporter(self.workbook_path, self.project_path)
        else:
            self.logger.error(f"No workbook found in {workbench_dir}")

    # ANCHOR: Sheet Opening Methods
    def open_stages_sheet(self) -> bool:
        """Open the Stages sheet for editing."""
        if not self.workbook_path:
            self.logger.error("No workbook path available")
            return False
            
        try:
            if os.name == 'nt':  # Windows
                os.startfile(self.workbook_path)
            elif os.name == 'posix':  # macOS and Linux
                subprocess.call(['open', self.workbook_path])
                
            self.logger.info("Opened Excel workbook for Stages sheet editing")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to open workbook: {str(e)}")
            return False
    
    def open_artifacts_sheet(self) -> bool:
        """Open the Artifacts sheet for editing."""
        return self.open_stages_sheet()  # Same operation - opens Excel
    
    def open_columns_sheet(self) -> bool:
        """Open the Columns sheet for editing."""
        return self.open_stages_sheet()  # Same operation - opens Excel

    # ANCHOR: Import and CSV Processing Methods
    def import_assign_columns(self, source_folder: str = None) -> bool:
        """
        Import and assign columns from source files.
        Delegates to the dedicated RawFileImporter module.
        
        Args:
            source_folder: Path to 1_sources folder (defaults to project's 1_sources)
            
        Returns:
            bool: True if import successful
        """
        if not self.raw_file_importer:
            self.logger.error("Raw file importer not initialized")
            return False
        
        return self.raw_file_importer.import_assign_columns(source_folder)

    # ANCHOR: AI Comment Generation Methods
    
    # ANCHOR: AI Comment Generation Methods
    def generate_ai_comments(self) -> bool:
        """Generate AI comments for artifacts and columns."""
        if not self.ai_workbench:
            self.logger.error("AI workbench manager not initialized")
            return False
        
        return self.ai_workbench.generate_all_ai_comments()

    def generate_artifact_ai_comments(self) -> bool:
        """Generate AI comments for artifacts only."""
        if not self.ai_workbench:
            self.logger.error("AI workbench manager not initialized")
            return False
        
        return self.ai_workbench.generate_artifact_comments()

    def generate_column_ai_comments(self) -> bool:
        """Generate AI comments for columns only."""
        if not self.ai_workbench:
            self.logger.error("AI workbench manager not initialized")
            return False
        
        return self.ai_workbench.generate_column_comments()

    def generate_readable_column_names(self) -> bool:
        """Generate human-readable column names for all columns."""
        if not self.ai_workbench:
            self.logger.error("AI workbench manager not initialized")
            return False
        
        return self.ai_workbench.generate_readable_column_names()

    def get_ai_comment_statistics(self) -> dict:
        """Get AI comment coverage statistics."""
        if not self.ai_workbench:
            self.logger.error("AI workbench manager not initialized")
            return {}
        
        return self.ai_workbench.get_ai_comment_statistics()

    def validate_ai_comments(self) -> dict:
        """Validate AI comment quality."""
        if not self.ai_workbench:
            self.logger.error("AI workbench manager not initialized")
            return {}
        
        return self.ai_workbench.validate_ai_comments()

    def is_ai_available(self) -> bool:
        """Check if AI functionality is available."""
        return self.ai_workbench and self.ai_workbench.is_ai_available()

    # ANCHOR: Cascade and Sync Operations
    def cascade_columns(self, artifact_id: int = None, include_technical_fields: bool = True) -> bool:
        """
        Perform deterministic column filling based on relations.
        
        Args:
            artifact_id: Optional specific artifact ID to cascade. If None, process all artifacts.
            include_technical_fields: Whether to include technical/audit columns
            
        Returns:
            bool: True if cascading was successful
        """
        if not self.cascading_engine:
            self.logger.error("Column cascading engine not initialized")
            return False
        
        try:
            if artifact_id:
                # Cascade for specific artifact
                return self.cascading_engine.cascade_columns_for_artifact(str(artifact_id), include_technical_fields)
            else:
                # Use the new correct cascading logic: find missing artifacts and cascade them
                return self.cascading_engine.cascade_all_missing_artifacts(include_technical_fields)
                
        except Exception as e:
            self.logger.error(f"Error during column cascading: {str(e)}")
            return False
    
    def cascade_columns_for_artifact(self, artifact_id, include_technical_fields: bool = True) -> bool:
        """
        Cascade columns for a specific artifact.
        
        Args:
            artifact_id: ID of the artifact to cascade columns for (string or int)
            include_technical_fields: Whether to include technical/audit columns
            
        Returns:
            bool: True if cascading was successful
        """
        if not self.cascading_engine:
            self.logger.error("Column cascading engine not initialized")
            return False
        
        return self.cascading_engine.cascade_columns_for_artifact(str(artifact_id), include_technical_fields)
    
    def create_cascading_config(self) -> bool:
        """
        Create cascading configuration file with default settings.
        
        Returns:
            bool: True if configuration was created successfully
        """
        if not self.cascading_engine:
            self.logger.error("Column cascading engine not initialized")
            return False
        
        return self.cascading_engine.create_cascading_config_file()
    
    def regenerate_all_columns(self, include_technical_fields: bool = True) -> bool:
        """
        Regenerate ALL columns with globally unique IDs and proper ordering.
        
        Args:
            include_technical_fields: Whether to include technical fields
            
        Returns:
            bool: True if regeneration was successful
        """
        if not self.cascading_engine:
            self.logger.error("Column cascading engine not initialized")
            return False
            
        return self.cascading_engine.regenerate_all_columns_with_unique_ids(include_technical_fields)

    def get_cascading_preview(self, artifact_id: int) -> dict:
        """
        Get a preview of what columns would be cascaded for an artifact.
        
        Args:
            artifact_id: ID of the artifact to preview cascading for
            
        Returns:
            dict: Preview information including column count and names
        """
        if not self.cascading_engine:
            return {"error": "Column cascading engine not initialized"}
        
        try:
            # Load artifacts data
            artifacts_df = self.excel_utils.read_sheet_data(self.workbook_path, "Artifacts")
            target_artifact = artifacts_df[artifacts_df['artifact_id'] == artifact_id]
            
            if target_artifact.empty:
                return {"error": f"Artifact {artifact_id} not found"}
            
            target_artifact = target_artifact.iloc[0]
            upstream_relation = target_artifact.get('upstream_relation', '')
            
            if not upstream_relation:
                return {"message": "No upstream relationship defined", "columns": []}
            
            # Get preview (this would be a new method in the cascading engine)
            preview = {
                "artifact_id": artifact_id,
                "artifact_name": target_artifact.get('artifact_name', ''),
                "upstream_relation": upstream_relation,
                "stage": target_artifact.get('stage_name', ''),
                "preview_note": f"Would cascade columns based on '{upstream_relation}' relationship"
            }
            
            return preview
            
        except Exception as e:
            return {"error": f"Error generating preview: {str(e)}"}
    
    def get_artifacts_with_upstream(self) -> List[Dict]:
        """
        Get list of artifacts that have upstream relationships.
        
        Returns:
            List[Dict]: List of artifacts with upstream relationships
        """
        try:
            artifacts_df = self.excel_utils.read_sheet_data(self.workbook_path, "Artifacts")
            if artifacts_df.empty:
                return []
            
            # Filter artifacts with upstream relationships
            artifacts_with_upstream = artifacts_df[
                artifacts_df['upstream_relation'].notna() & 
                (artifacts_df['upstream_relation'] != '')
            ]
            
            return artifacts_with_upstream[['artifact_id', 'artifact_name', 'stage_name', 'upstream_relation']].to_dict('records')
            
        except Exception as e:
            self.logger.error(f"Error getting artifacts with upstream relationships: {str(e)}")
            return []
    
    def sync_and_validate(self) -> dict:
        """
        Sync all sheets and run validations.
        
        Returns:
            dict: Validation results and errors
        """
        # TODO: Implement sync and validation logic
        self.logger.info("Sync and validation - implementation pending")
        return {"status": "pending"}

    # ANCHOR: Workbook Management Methods
    def save_workbook(self) -> bool:
        """Save the current workbook version."""
        try:
            # Create backup first
            if self.workbook_path and os.path.exists(self.workbook_path):
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"workbench_backup_{timestamp}.xlsx"
                backup_path = os.path.join(os.path.dirname(self.workbook_path), backup_name)
                
                import shutil
                shutil.copy2(self.workbook_path, backup_path)
                self.logger.info(f"Created backup: {backup_name}")
                
            self.logger.info("Workbook saved successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save workbook: {str(e)}")
            return False
