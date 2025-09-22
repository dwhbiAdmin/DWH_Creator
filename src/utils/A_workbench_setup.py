#!/usr/bin/env python3
"""
Workbench Setup Module for DWH Creator
Created: September 22, 2025
Purpose: Handle setup of workbench sheets (stages, artifacts, columns) with embedded default structure
Similar to workbench_configuration_setup.py but for actual workbench files

This module creates and manages the workbench Excel files that contain:
- Stages sheet: Stage definitions and metadata
- Artifacts sheet: Artifact definitions for each stage  
- Columns sheet: Column definitions and cascading rules

Structure is based on the established workbench patterns and will NOT be changed without permission.
"""

import os
import logging
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('DWH_Creator')


class WorkbenchSetupManager:
    """
    Manages creation and setup of workbench Excel files with embedded default structure.
    Similar to WorkbenchConfigurationManager but for actual workbench operations.
    """
    
    def __init__(self):
        """Initialize the WorkbenchSetupManager."""
        self.default_structure_loaded = True
        logger.info("WorkbenchSetupManager initialized with embedded default structure")
    
    def create_project_workbench_file(self, file_path: str, project_name: str) -> bool:
        """
        Create a new workbench Excel file with default structure.
        
        Args:
            file_path (str): Path where the workbench file will be created
            project_name (str): Name of the project for metadata
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create the workbench sheets with embedded data
            stages_df = self._create_stages_sheet()
            artifacts_df = self._create_artifacts_sheet()
            columns_df = self._create_columns_sheet()
            
            # Write to Excel with proper sheet order
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # Write sheets in logical order: stages → artifacts → columns
                stages_df.to_excel(writer, sheet_name='stages', index=False)
                artifacts_df.to_excel(writer, sheet_name='artifacts', index=False)  
                columns_df.to_excel(writer, sheet_name='columns', index=False)
                
                # Apply formatting
                self._apply_workbench_formatting(writer)
            
            logger.info(f"Created project-specific workbench file: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create workbench file {file_path}: {str(e)}")
            return False
    
    def create_default_workbench_file(self, config_path: str = "workbench_default.xlsx") -> bool:
        """
        Create a default workbench file in the current directory.
        
        Args:
            config_path (str): Path for the default workbench file
            
        Returns:
            bool: True if successful, False otherwise
        """
        return self.create_project_workbench_file(config_path, "DefaultWorkbench")
    
    def _create_stages_sheet(self) -> pd.DataFrame:
        """Create stages sheet structure with empty data.
        Only column headers, ready for user to populate.
        Structure matches workbench requirements - DO NOT CHANGE WITHOUT PERMISSION."""
        
        # Define column structure for stages sheet - exact order as specified by user
        stages_columns = [
            'stage_id', 
            'stage_name', 
            'platform',
            'artifact_side',
            'stage_description',
            'processing_order',
            'is_active',
            'default_artifact_type',
            'technical_fields_required',
            'partition_strategy',
            'notes'
        ]
        
        # Return empty DataFrame with just the column structure
        return pd.DataFrame(columns=stages_columns)
    
    def _create_artifacts_sheet(self) -> pd.DataFrame:
        """Create artifacts sheet structure with empty data.
        Only column headers, ready for user to populate.
        Structure matches workbench requirements - DO NOT CHANGE WITHOUT PERMISSION."""
        
        # Define column structure for artifacts sheet - exact order as specified by user
        artifacts_columns = [
            'stage_id',
            'stage_name',
            'artifact_id',
            'artifact_name',
            'artifact_type',
            'artifact_topology',
            'upstream_relations',
            'upstream_relation',
            'relation_type',
            'artifact_relation_direction',
            'artifact_domain',
            'artifact_comment',
            'ddl_template',
            'etl_template'
        ]
        
        # Return empty DataFrame with just the column structure
        return pd.DataFrame(columns=artifacts_columns)
    
    def _create_columns_sheet(self) -> pd.DataFrame:
        """Create columns sheet structure with empty data.
        Only column headers, ready for user to populate.
        Structure matches workbench requirements - DO NOT CHANGE WITHOUT PERMISSION."""
        
        # Define column structure for columns sheet - exact order as specified
        columns_columns = [
            'stage_id',
            'stage_name',
            'artifact_id',
            'artifact_name',
            'column_id',
            'column_name',
            'data_type',
            'order',
            'column_business_name',
            'column_group',
            'column_comment'
        ]
        
        # Return empty DataFrame with just the column structure
        return pd.DataFrame(columns=columns_columns)
    
    def _apply_workbench_formatting(self, writer):
        """Apply formatting to the workbench Excel sheets.
        Includes light grey formatting for lookup columns (including headers), freeze panes, and autofilter."""
        try:
            from openpyxl.styles import PatternFill
            
            # Light grey fill for lookup columns
            light_grey_fill = PatternFill(start_color='D3D3D3', end_color='D3D3D3', fill_type='solid')
            
            # Get workbooks for formatting
            workbook = writer.book
            
            # Format stages sheet
            if 'stages' in workbook.sheetnames:
                stages_sheet = workbook['stages']
                # Freeze first row
                stages_sheet.freeze_panes = 'A2'
                # Add autofilter to first row
                stages_sheet.auto_filter.ref = stages_sheet.dimensions
                # Apply light grey to stage_name column (column B) - including header
                for row in range(1, stages_sheet.max_row + 1):  # Start from row 1 to include header
                    cell = stages_sheet.cell(row=row, column=2)  # column B
                    cell.fill = light_grey_fill
            
            # Format artifacts sheet
            if 'artifacts' in workbook.sheetnames:
                artifacts_sheet = workbook['artifacts']
                # Freeze first row
                artifacts_sheet.freeze_panes = 'A2'
                # Add autofilter to first row
                artifacts_sheet.auto_filter.ref = artifacts_sheet.dimensions
                # Apply light grey to stage_name column (column B) - including header
                for row in range(1, artifacts_sheet.max_row + 1):  # Start from row 1 to include header
                    cell = artifacts_sheet.cell(row=row, column=2)  # column B
                    cell.fill = light_grey_fill
            
            # Format columns sheet
            if 'columns' in workbook.sheetnames:
                columns_sheet = workbook['columns']
                # Freeze first row
                columns_sheet.freeze_panes = 'A2'
                # Add autofilter to first row
                columns_sheet.auto_filter.ref = columns_sheet.dimensions
                # Apply light grey to lookup columns - including headers
                for row in range(1, columns_sheet.max_row + 1):  # Start from row 1 to include header
                    # stage_name column (column B)
                    cell_stage = columns_sheet.cell(row=row, column=2)  # column B
                    cell_stage.fill = light_grey_fill
                    # artifact_name column (column D)
                    cell_artifact = columns_sheet.cell(row=row, column=4)  # column D
                    cell_artifact.fill = light_grey_fill
            
            logger.info("Applied workbench formatting including freeze panes, autofilter, and light grey for lookup columns (including headers)")
            
        except ImportError:
            logger.warning("openpyxl not available for formatting")
        except Exception as e:
            logger.warning(f"Could not apply workbench formatting: {str(e)}")


def create_default_workbench(output_path: str = "workbench_default.xlsx") -> bool:
    """
    Convenience function to create a default workbench file.
    
    Args:
        output_path (str): Path for the output file
        
    Returns:
        bool: True if successful, False otherwise
    """
    manager = WorkbenchSetupManager()
    return manager.create_default_workbench_file(output_path)


if __name__ == "__main__":
    # Example usage
    print("Creating default workbench file...")
    success = create_default_workbench("workbench_example.xlsx")
    if success:
        print("✅ Default workbench file created successfully!")
    else:
        print("❌ Failed to create default workbench file")