"""
Cascade Enhancements Module
============================

This module provides enhancement operations to be run after cascade operations.
It includes cleanup of duplicates and re-enumeration of column IDs.
"""

import pandas as pd
from pathlib import Path
import sys

# Add src directory to path for imports
current_dir = Path(__file__).parent
src_dir = current_dir.parent.parent.parent
sys.path.insert(0, str(src_dir))

from utils.c_workbench_excel_utils import ExcelUtils
from utils.z_logger import Logger


class CascadeEnhancements:
    """Handles post-cascade enhancement operations."""
    
    def __init__(self, workbook_path: str):
        """
        Initialize the Cascade Enhancements.
        
        Args:
            workbook_path: Path to the workbook Excel file
        """
        self.workbook_path = workbook_path
        self.excel_utils = ExcelUtils()
        self.logger = Logger()
    
    def run_all_enhancements(self):
        """
        Run all enhancement operations in sequence.
        
        This is the main method that should be called after cascade operations.
        It runs:
        1. Cleanup duplicate columns
        2. Re-enumerate column IDs
        """
        try:
            self.logger.info("Starting cascade enhancements...")
            
            # Step 1: Clean up duplicate columns
            self.cleanup_duplicate_columns()
            
            # Step 2: Re-enumerate column IDs
            self.reenumerate_column_ids()
            
            self.logger.info("All cascade enhancements completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error in cascade enhancements: {str(e)}")
            raise
    
    def cleanup_duplicate_columns(self):
        """
        Clean up duplicate column names within each artifact.
        Keeps the first occurrence and removes subsequent duplicates.
        """
        try:
            self.logger.info("Step 1: Cleaning up duplicate columns...")
            
            # Read current columns sheet
            df_columns = pd.read_excel(self.workbook_path, sheet_name='columns')
            
            if df_columns.empty:
                self.logger.info("  No columns to clean up")
                return
            
            initial_count = len(df_columns)
            self.logger.info(f"  Initial column count: {initial_count}")
            
            # Group by artifact_id and remove duplicates within each group
            artifacts = df_columns['artifact_id'].unique()
            
            cleaned_rows = []
            total_duplicates_removed = 0
            
            for artifact_id in artifacts:
                artifact_rows = df_columns[df_columns['artifact_id'] == artifact_id]
                
                # Find duplicates based on column_name within this artifact
                before_count = len(artifact_rows)
                
                # Keep first occurrence, remove duplicates
                artifact_rows_cleaned = artifact_rows.drop_duplicates(
                    subset=['artifact_id', 'column_name'], 
                    keep='first'
                )
                
                after_count = len(artifact_rows_cleaned)
                duplicates_removed = before_count - after_count
                
                if duplicates_removed > 0:
                    self.logger.info(f"  Artifact {artifact_id}: Removed {duplicates_removed} duplicate column(s)")
                    total_duplicates_removed += duplicates_removed
                
                cleaned_rows.append(artifact_rows_cleaned)
            
            # Combine all cleaned artifacts
            df_cleaned = pd.concat(cleaned_rows, ignore_index=True)
            
            final_count = len(df_cleaned)
            self.logger.info(f"  Final column count: {final_count}")
            self.logger.info(f"  Total duplicates removed: {total_duplicates_removed}")
            
            if total_duplicates_removed > 0:
                # Write cleaned data back to Excel
                self._write_columns_to_excel(df_cleaned)
                self.logger.info("  Cleanup completed successfully")
            else:
                self.logger.info("  No duplicates found, no cleanup needed")
                
        except Exception as e:
            self.logger.error(f"Error during duplicate cleanup: {str(e)}")
            raise
    
    def reenumerate_column_ids(self):
        """
        Re-enumerate column IDs to be sequential (c_1, c_2, c_3, etc.).
        This should be run at the end of all enhancements.
        """
        try:
            self.logger.info("Step 2: Re-enumerating column IDs...")
            
            # Read current columns sheet
            df_columns = pd.read_excel(self.workbook_path, sheet_name='columns')
            
            if df_columns.empty:
                self.logger.info("  No columns to re-enumerate")
                return
            
            initial_first_id = df_columns.iloc[0]['column_id'] if len(df_columns) > 0 else None
            initial_last_id = df_columns.iloc[-1]['column_id'] if len(df_columns) > 0 else None
            
            self.logger.info(f"  Current column IDs: {initial_first_id} to {initial_last_id}")
            
            # Re-enumerate column IDs sequentially
            for idx, row_idx in enumerate(df_columns.index, start=1):
                df_columns.at[row_idx, 'column_id'] = f"c_{idx}"
            
            final_first_id = df_columns.iloc[0]['column_id']
            final_last_id = df_columns.iloc[-1]['column_id']
            
            self.logger.info(f"  Re-enumerated column IDs: {final_first_id} to {final_last_id}")
            self.logger.info(f"  Total columns: {len(df_columns)}")
            
            # Write re-enumerated data back to Excel
            self._write_columns_to_excel(df_columns)
            self.logger.info("  Re-enumeration completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error during column ID re-enumeration: {str(e)}")
            raise
    
    def _write_columns_to_excel(self, df_columns: pd.DataFrame):
        """
        Write columns DataFrame back to Excel, replacing the columns sheet.
        
        Args:
            df_columns: DataFrame containing the columns data
        """
        try:
            from openpyxl import load_workbook
            
            wb = load_workbook(self.workbook_path)
            
            # Remove old columns sheet
            if 'columns' in wb.sheetnames:
                del wb['columns']
            
            # Create new columns sheet at position 2 (after stages and artifacts)
            ws = wb.create_sheet('columns', 2)
            
            # Write headers
            headers = df_columns.columns.tolist()
            for col_idx, header in enumerate(headers, start=1):
                ws.cell(row=1, column=col_idx, value=header)
            
            # Write data
            for row_idx, row_data in enumerate(df_columns.values, start=2):
                for col_idx, value in enumerate(row_data, start=1):
                    ws.cell(row=row_idx, column=col_idx, value=value)
            
            wb.save(self.workbook_path)
            
        except Exception as e:
            self.logger.error(f"Error writing to Excel: {str(e)}")
            raise


def main():
    """Main function for testing cascade enhancements."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python b_cascade_enhancements.py <workbook_path>")
        sys.exit(1)
    
    workbook_path = sys.argv[1]
    
    enhancements = CascadeEnhancements(workbook_path)
    enhancements.run_all_enhancements()


if __name__ == "__main__":
    main()
