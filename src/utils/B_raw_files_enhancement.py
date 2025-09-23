"""
Raw Files Enhancement Module
===========================

Module for enhancing imported raw files with:
1. AI-generated column comments
2. AI-generated artifact comments  
3. Deterministic primary key detection
4. AI-generated business names for columns

This module consolidates all post-import enhancement operations.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import re
from collections import Counter

# Import project utilities
from utils.logger import Logger
from utils.B_worksheet_config_manager import ConfigManager
from utils.B_excel_utils import ExcelUtils
from backend.Y_ai_manager import AIWorkbenchManager


class RawFilesEnhancer:
    """
    Main class for enhancing imported raw files.
    
    Provides comprehensive enhancement including:
    - AI-generated column comments
    - AI-generated artifact comments
    - Deterministic primary key detection
    - AI-generated business names
    """
    
    def __init__(self, workbook_path: str, api_key: Optional[str] = None):
        """
        Initialize the Raw Files Enhancer.
        
        Args:
            workbook_path: Path to the workbook file
            api_key: Optional API key for AI services
        """
        self.logger = Logger()
        self.config_manager = ConfigManager()
        self.excel_utils = ExcelUtils()
        self.workbook_path = workbook_path
        
        # Initialize AI manager if API key provided
        self.ai_manager = None
        if api_key:
            try:
                self.ai_manager = AIWorkbenchManager(workbook_path, api_key)
                self.logger.info("AI manager initialized successfully")
            except Exception as e:
                self.logger.warning(f"Could not initialize AI manager: {str(e)}")
        
        # Configuration for primary key detection
        self.pk_detection_config = {
            "min_uniqueness_ratio": 0.95,  # Minimum uniqueness for PK consideration
            "max_null_ratio": 0.05,        # Maximum null percentage for PK
        }
        
        # Patterns for identifying key columns by name
        self.key_patterns = [
            r".*_?id$", r".*_?key$", r".*_?pk$", 
            r"^id$", r"^key$", r"^pk$",
            r".*_?identifier$", r".*_?number$"
        ]
        
        self.logger.info("RawFilesEnhancer initialized successfully")
    
    def enhance_all_raw_files(self) -> bool:
        """
        Perform all enhancement operations on imported raw files.
        
        Returns:
            bool: True if all enhancements completed successfully
        """
        self.logger.info("Starting comprehensive enhancement of raw files")
        
        try:
            # Step 1: Generate AI comments for artifacts
            self.logger.info("Step 1: Generating AI comments for artifacts...")
            artifact_success = self.generate_artifact_comments()
            
            # Step 2: Generate AI comments for columns
            self.logger.info("Step 2: Generating AI comments for columns...")
            column_comments_success = self.generate_column_comments()
            
            # Step 3: Determine primary keys deterministically
            self.logger.info("Step 3: Determining primary keys...")
            pk_success = self.determine_primary_keys()
            
            # Step 4: Generate AI business names for columns
            self.logger.info("Step 4: Generating business names for columns...")
            business_names_success = self.generate_business_names()
            
            # Check overall success
            overall_success = all([
                artifact_success, 
                column_comments_success, 
                pk_success, 
                business_names_success
            ])
            
            if overall_success:
                self.logger.info("✅ All enhancement operations completed successfully!")
            else:
                self.logger.warning("⚠️ Some enhancement operations had issues. Check logs for details.")
            
            return overall_success
            
        except Exception as e:
            self.logger.error(f"Error during enhancement process: {str(e)}")
            return False
    
    def generate_artifact_comments(self) -> bool:
        """Generate AI comments for artifacts."""
        try:
            if not self.ai_manager:
                self.logger.warning("AI manager not available. Skipping artifact comments.")
                return True  # Not a failure, just skip
            
            success = self.ai_manager.generate_artifact_comments()
            if success:
                self.logger.info("✅ Artifact comments generated successfully")
            else:
                self.logger.warning("⚠️ Some artifact comments could not be generated")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error generating artifact comments: {str(e)}")
            return False
    
    def generate_column_comments(self) -> bool:
        """Generate AI comments for columns."""
        try:
            if not self.ai_manager:
                self.logger.warning("AI manager not available. Skipping column comments.")
                return True  # Not a failure, just skip
            
            success = self.ai_manager.generate_column_comments()
            if success:
                self.logger.info("✅ Column comments generated successfully")
            else:
                self.logger.warning("⚠️ Some column comments could not be generated")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error generating column comments: {str(e)}")
            return False
    
    def determine_primary_keys(self) -> bool:
        """Deterministically identify and set primary keys for all column sheets."""
        try:
            # Get all column sheet names
            column_sheets = self._get_column_sheet_names()
            
            if not column_sheets:
                self.logger.warning("No column sheets found to analyze for primary keys")
                return True
            
            updated_sheets = 0
            
            for sheet_name in column_sheets:
                try:
                    # Read the column sheet
                    columns_df = self.excel_utils.read_sheet_data(self.workbook_path, sheet_name)
                    
                    if columns_df.empty:
                        self.logger.warning(f"Sheet {sheet_name} is empty, skipping")
                        continue
                    
                    # Analyze and update primary keys for this sheet
                    pk_candidates = self._analyze_primary_key_candidates(columns_df, sheet_name)
                    
                    if pk_candidates:
                        # Update the column_group for primary key columns
                        updated_df = self._update_primary_key_groups(columns_df, pk_candidates)
                        
                        # Write back to Excel
                        write_success = self.excel_utils.write_sheet_data(
                            self.workbook_path, sheet_name, updated_df
                        )
                        
                        if write_success:
                            updated_sheets += 1
                            pk_cols = ", ".join(pk_candidates)
                            self.logger.info(f"✅ Primary key(s) identified for {sheet_name}: {pk_cols}")
                        else:
                            self.logger.error(f"Failed to write primary key updates to {sheet_name}")
                    else:
                        self.logger.info(f"No clear primary key candidates found for {sheet_name}")
                
                except Exception as e:
                    self.logger.error(f"Error analyzing primary keys for {sheet_name}: {str(e)}")
                    continue
            
            self.logger.info(f"✅ Primary key analysis completed. Updated {updated_sheets} sheets.")
            return True
            
        except Exception as e:
            self.logger.error(f"Error in primary key determination: {str(e)}")
            return False
    
    def generate_business_names(self) -> bool:
        """Generate AI business names for columns."""
        try:
            if not self.ai_manager:
                self.logger.warning("AI manager not available. Generating simple business names.")
                return self._generate_simple_business_names()
            
            success = self.ai_manager.generate_readable_column_names()
            if success:
                self.logger.info("✅ Business names generated successfully")
            else:
                self.logger.warning("⚠️ Some business names could not be generated")
                # Fallback to simple business names
                return self._generate_simple_business_names()
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error generating business names: {str(e)}")
            # Fallback to simple business names
            return self._generate_simple_business_names()
    
    def _get_column_sheet_names(self) -> List[str]:
        """Get all column sheet names from the workbook."""
        try:
            from openpyxl import load_workbook
            
            wb = load_workbook(self.workbook_path, read_only=True)
            column_sheets = [sheet for sheet in wb.sheetnames if sheet.startswith('Columns')]
            wb.close()
            
            return column_sheets
            
        except Exception as e:
            self.logger.error(f"Error getting column sheet names: {str(e)}")
            return []
    
    def _analyze_primary_key_candidates(self, columns_df: pd.DataFrame, sheet_name: str) -> List[str]:
        """Analyze a column sheet to identify primary key candidates."""
        try:
            # First, get the actual data from the source to analyze uniqueness
            # For now, we'll use heuristics based on column names and types
            
            pk_candidates = []
            
            # Check each column for primary key characteristics
            for _, row in columns_df.iterrows():
                column_name = row.get('Column Name', '')
                data_type = row.get('Data Type', '')
                column_group = row.get('Column Group', '')
                
                # Skip if already marked as primary key
                if column_group == 'primary_key':
                    continue
                
                # Check name patterns
                col_lower = column_name.lower()
                is_key_pattern = any(re.match(pattern, col_lower) for pattern in self.key_patterns)
                
                # Check data type (prefer integer or string IDs)
                is_appropriate_type = any(dt in data_type.upper() for dt in ['INT', 'BIGINT', 'VARCHAR', 'STRING'])
                
                # Score the candidate
                score = 0
                if is_key_pattern:
                    score += 3
                if is_appropriate_type:
                    score += 2
                if 'id' in col_lower:
                    score += 2
                if col_lower in ['id', 'key', 'pk']:
                    score += 3
                
                # Consider as primary key candidate if score is high enough
                if score >= 4:
                    pk_candidates.append(column_name)
                    self.logger.info(f"Primary key candidate found: {column_name} (score: {score})")
            
            # If multiple candidates, prefer the one with the highest score/best name
            if len(pk_candidates) > 1:
                # Prefer columns with simpler names
                preferred = None
                for candidate in pk_candidates:
                    col_lower = candidate.lower()
                    if col_lower in ['id', 'key', 'pk']:
                        preferred = candidate
                        break
                    elif col_lower.endswith('_id') and not preferred:
                        preferred = candidate
                
                if preferred:
                    pk_candidates = [preferred]
                else:
                    # Take the first one
                    pk_candidates = pk_candidates[:1]
            
            return pk_candidates
            
        except Exception as e:
            self.logger.error(f"Error analyzing primary key candidates for {sheet_name}: {str(e)}")
            return []
    
    def _update_primary_key_groups(self, columns_df: pd.DataFrame, pk_candidates: List[str]) -> pd.DataFrame:
        """Update the column_group for primary key columns."""
        updated_df = columns_df.copy()
        
        # Update the Column Group for primary key candidates
        mask = updated_df['Column Name'].isin(pk_candidates)
        updated_df.loc[mask, 'Column Group'] = 'primary_key'
        
        return updated_df
    
    def _generate_simple_business_names(self) -> bool:
        """Generate simple business names without AI (fallback method)."""
        try:
            # Get all column sheet names
            column_sheets = self._get_column_sheet_names()
            
            if not column_sheets:
                self.logger.warning("No column sheets found for business name generation")
                return True
            
            updated_sheets = 0
            
            for sheet_name in column_sheets:
                try:
                    # Read the column sheet
                    columns_df = self.excel_utils.read_sheet_data(self.workbook_path, sheet_name)
                    
                    if columns_df.empty:
                        continue
                    
                    # Generate simple business names
                    updated_df = columns_df.copy()
                    
                    for idx, row in updated_df.iterrows():
                        column_name = row.get('Column Name', '')
                        current_business_name = row.get('Column Business Name', '')
                        
                        # Only generate if business name is empty
                        if pd.isna(current_business_name) or current_business_name.strip() == '':
                            business_name = self._create_simple_business_name(column_name)
                            updated_df.at[idx, 'Column Business Name'] = business_name
                    
                    # Write back to Excel
                    write_success = self.excel_utils.write_sheet_data(
                        self.workbook_path, sheet_name, updated_df
                    )
                    
                    if write_success:
                        updated_sheets += 1
                
                except Exception as e:
                    self.logger.error(f"Error generating business names for {sheet_name}: {str(e)}")
                    continue
            
            self.logger.info(f"✅ Simple business names generated for {updated_sheets} sheets")
            return True
            
        except Exception as e:
            self.logger.error(f"Error generating simple business names: {str(e)}")
            return False
    
    def _create_simple_business_name(self, column_name: str) -> str:
        """Create a simple business name from column name."""
        # Convert snake_case and camelCase to Title Case
        business_name = re.sub(r'([a-z])([A-Z])', r'\1 \2', column_name)  # camelCase
        business_name = business_name.replace('_', ' ')  # snake_case
        business_name = business_name.title()  # Title case
        
        # Clean up common abbreviations
        replacements = {
            ' Id': ' ID',
            ' Pk': ' Primary Key',
            ' Fk': ' Foreign Key',
            ' Dt': ' Date',
            ' Ts': ' Timestamp',
            ' Qty': ' Quantity',
            ' Amt': ' Amount',
            ' Desc': ' Description',
            ' Addr': ' Address',
            ' Num': ' Number',
            ' Cd': ' Code'
        }
        
        for old, new in replacements.items():
            business_name = business_name.replace(old, new)
        
        return business_name


def enhance_raw_files(workbook_path: str, api_key: Optional[str] = None) -> bool:
    """
    Convenience function to enhance raw files.
    
    Args:
        workbook_path: Path to the workbook file
        api_key: Optional API key for AI services
        
    Returns:
        bool: True if enhancement completed successfully
    """
    enhancer = RawFilesEnhancer(workbook_path, api_key)
    return enhancer.enhance_all_raw_files()