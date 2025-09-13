"""
AI Workbench Manager
===================

Handles all AI-powered operations for the workbench including comment generation
for artifacts and columns. Separated from main workbench manager for better
organization and reusability.
"""

# ANCHOR: Imports and Dependencies
import pandas as pd
from pathlib import Path
import sys
from typing import Optional

# Import utilities with proper path handling
current_dir = Path(__file__).parent
src_dir = current_dir.parent
sys.path.insert(0, str(src_dir))

from utils.ai_comment_generator import AICommentGenerator
from utils.excel_utils import ExcelUtils
from utils.logger import Logger

# ANCHOR: AIWorkbenchManager Class Definition
class AIWorkbenchManager:
    """
    Manages AI-powered operations for Excel workbench data.
    """
    
    # ANCHOR: Initialization and Setup
    def __init__(self, workbook_path: str, openai_api_key: str = None):
        """
        Initialize the AI Workbench Manager.
        
        Args:
            workbook_path: Path to the Excel workbook
            openai_api_key: OpenAI API key for AI comment generation
        """
        self.workbook_path = workbook_path
        self.excel_utils = ExcelUtils()
        self.ai_generator = AICommentGenerator(api_key=openai_api_key)
        self.logger = Logger()
    
    def is_ai_available(self) -> bool:
        """Check if AI functionality is available."""
        return self.ai_generator.is_available()

    # ANCHOR: Public AI Comment Generation Methods
    def generate_all_ai_comments(self) -> bool:
        """Generate AI comments for both artifacts and columns."""
        if not self.is_ai_available():
            self.logger.warning("AI comment generation not available - no OpenAI API key")
            return False
        
        try:
            success = True
            
            # Generate artifact comments
            self.logger.info("Generating AI comments for artifacts...")
            artifact_success = self.generate_artifact_comments()
            
            # Generate column comments  
            self.logger.info("Generating AI comments for columns...")
            column_success = self.generate_column_comments()
            
            return artifact_success and column_success
            
        except Exception as e:
            self.logger.error(f"Failed to generate AI comments: {str(e)}")
            return False

    def generate_artifact_comments(self) -> bool:
        """Generate AI comments for artifacts only."""
        if not self.is_ai_available():
            self.logger.warning("AI comment generation not available - no OpenAI API key")
            return False
        
        try:
            self.logger.info("Generating AI comments for artifacts...")
            return self._generate_artifact_comments()
            
        except Exception as e:
            self.logger.error(f"Failed to generate artifact AI comments: {str(e)}")
            return False

    def generate_column_comments(self) -> bool:
        """Generate AI comments for columns only."""
        if not self.is_ai_available():
            self.logger.warning("AI comment generation not available - no OpenAI API key")
            return False
        
        try:
            self.logger.info("Generating AI comments for columns...")
            return self._generate_column_comments()
            
        except Exception as e:
            self.logger.error(f"Failed to generate column AI comments: {str(e)}")
            return False

    # ANCHOR: Private AI Generation Helper Methods
    def _generate_artifact_comments(self) -> bool:
        """Generate AI comments for artifacts."""
        try:
            artifacts_df = self.excel_utils.read_sheet_data(self.workbook_path, "Artifacts")
            if artifacts_df.empty:
                self.logger.info("No artifacts found to generate comments for")
                return True
            
            # Count artifacts needing comments
            artifacts_needing_comments = []
            for idx, row in artifacts_df.iterrows():
                if pd.isna(row.get('Artifact Comment', '')) or row.get('Artifact Comment', '') == '':
                    artifact_name = row.get('Artifact Name', '')
                    if artifact_name:
                        artifacts_needing_comments.append((idx, artifact_name, row.get('Stage Name', '')))
            
            if not artifacts_needing_comments:
                self.logger.info("All artifacts already have comments")
                return True
            
            self.logger.info(f"Generating comments for {len(artifacts_needing_comments)} artifacts...")
            
            # Generate comments for artifacts that don't have them
            updated = False
            success_count = 0
            
            for idx, artifact_name, stage_name in artifacts_needing_comments:
                try:
                    comment = self.ai_generator.generate_artifact_comment(artifact_name, stage_name)
                    if comment:
                        artifacts_df.at[idx, 'Artifact Comment'] = comment
                        updated = True
                        success_count += 1
                        self.logger.info(f"Generated comment for {artifact_name}: {comment}")
                    else:
                        self.logger.warning(f"No comment generated for {artifact_name}")
                except Exception as e:
                    self.logger.error(f"Error generating comment for {artifact_name}: {str(e)}")
            
            if updated:
                write_success = self.excel_utils.write_sheet_data(self.workbook_path, "Artifacts", artifacts_df)
                if write_success:
                    self.logger.info(f"Successfully generated {success_count}/{len(artifacts_needing_comments)} artifact comments")
                return write_success
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error generating artifact comments: {str(e)}")
            return False

    def _generate_column_comments(self) -> bool:
        """Generate AI comments for columns."""
        try:
            columns_df = self.excel_utils.read_sheet_data(self.workbook_path, "Columns")
            if columns_df.empty:
                self.logger.info("No columns found to generate comments for")
                return True
            
            # Count columns needing comments
            columns_needing_comments = []
            for idx, row in columns_df.iterrows():
                if pd.isna(row.get('Column Comment', '')) or row.get('Column Comment', '') == '':
                    column_name = row.get('Column Name', '')
                    if column_name:
                        columns_needing_comments.append((idx, column_name, row.get('Data Type', ''), row.get('Artifact ID', '')))
            
            if not columns_needing_comments:
                self.logger.info("All columns already have comments")
                return True
            
            self.logger.info(f"Generating comments for {len(columns_needing_comments)} columns...")
            
            # Generate comments for columns that don't have them
            updated = False
            success_count = 0
            
            for idx, column_name, data_type, artifact_id in columns_needing_comments:
                try:
                    comment = self.ai_generator.generate_column_comment(column_name, data_type, artifact_id)
                    if comment:
                        columns_df.at[idx, 'Column Comment'] = comment
                        updated = True
                        success_count += 1
                        self.logger.info(f"Generated comment for {column_name}: {comment}")
                    else:
                        self.logger.warning(f"No comment generated for {column_name}")
                except Exception as e:
                    self.logger.error(f"Error generating comment for {column_name}: {str(e)}")
            
            if updated:
                write_success = self.excel_utils.write_sheet_data(self.workbook_path, "Columns", columns_df)
                if write_success:
                    self.logger.info(f"Successfully generated {success_count}/{len(columns_needing_comments)} column comments")
                return write_success
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error generating column comments: {str(e)}")
            return False

    # ANCHOR: AI Analytics and Reporting Methods
    def get_ai_comment_statistics(self) -> dict:
        """
        Get statistics about AI comment coverage.
        
        Returns:
            dict: Statistics about comment coverage
        """
        try:
            stats = {
                'artifacts': {'total': 0, 'with_comments': 0, 'coverage_percent': 0},
                'columns': {'total': 0, 'with_comments': 0, 'coverage_percent': 0}
            }
            
            # Artifact statistics
            artifacts_df = self.excel_utils.read_sheet_data(self.workbook_path, "Artifacts")
            if not artifacts_df.empty:
                stats['artifacts']['total'] = len(artifacts_df)
                with_comments = artifacts_df[
                    artifacts_df['Artifact Comment'].notna() & 
                    (artifacts_df['Artifact Comment'] != '')
                ]
                stats['artifacts']['with_comments'] = len(with_comments)
                if stats['artifacts']['total'] > 0:
                    stats['artifacts']['coverage_percent'] = round(
                        (stats['artifacts']['with_comments'] / stats['artifacts']['total']) * 100, 1
                    )
            
            # Column statistics
            columns_df = self.excel_utils.read_sheet_data(self.workbook_path, "Columns")
            if not columns_df.empty:
                stats['columns']['total'] = len(columns_df)
                with_comments = columns_df[
                    columns_df['Column Comment'].notna() & 
                    (columns_df['Column Comment'] != '')
                ]
                stats['columns']['with_comments'] = len(with_comments)
                if stats['columns']['total'] > 0:
                    stats['columns']['coverage_percent'] = round(
                        (stats['columns']['with_comments'] / stats['columns']['total']) * 100, 1
                    )
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting AI comment statistics: {str(e)}")
            return {}

    # ANCHOR: AI Quality and Validation Methods
    def validate_ai_comments(self) -> dict:
        """
        Validate the quality of AI-generated comments.
        
        Returns:
            dict: Validation results
        """
        try:
            validation_results = {
                'artifacts': {'valid': 0, 'too_short': 0, 'empty': 0},
                'columns': {'valid': 0, 'too_short': 0, 'empty': 0}
            }
            
            # Validate artifact comments
            artifacts_df = self.excel_utils.read_sheet_data(self.workbook_path, "Artifacts")
            if not artifacts_df.empty:
                for _, row in artifacts_df.iterrows():
                    comment = str(row.get('Artifact Comment', ''))
                    if not comment or comment == 'nan':
                        validation_results['artifacts']['empty'] += 1
                    elif len(comment.strip()) < 10:
                        validation_results['artifacts']['too_short'] += 1
                    else:
                        validation_results['artifacts']['valid'] += 1
            
            # Validate column comments
            columns_df = self.excel_utils.read_sheet_data(self.workbook_path, "Columns")
            if not columns_df.empty:
                for _, row in columns_df.iterrows():
                    comment = str(row.get('Column Comment', ''))
                    if not comment or comment == 'nan':
                        validation_results['columns']['empty'] += 1
                    elif len(comment.strip()) < 10:
                        validation_results['columns']['too_short'] += 1
                    else:
                        validation_results['columns']['valid'] += 1
            
            return validation_results
            
        except Exception as e:
            self.logger.error(f"Error validating AI comments: {str(e)}")
            return {}
