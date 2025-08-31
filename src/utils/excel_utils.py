"""
Excel Utilities
===============

Excel-specific operations and helpers.
"""

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.worksheet.table import Table, TableStyleInfo
import os

class ExcelUtils:
    """Excel workbook and worksheet utility functions."""
    
    @staticmethod
    def create_workbook_with_sheets(file_path: str, sheets_config: dict) -> bool:
        """
        Create Excel workbook with specified sheets and headers.
        
        Args:
            file_path: Path where to create the workbook
            sheets_config: Dictionary with sheet configurations
            
        Returns:
            bool: True if workbook created successfully
        """
        try:
            # Create new workbook
            wb = Workbook()
            
            # Remove default sheet
            if 'Sheet' in wb.sheetnames:
                wb.remove(wb['Sheet'])
            
            # Create each sheet
            for sheet_name, config in sheets_config.items():
                ws = wb.create_sheet(title=sheet_name)
                
                # Add headers
                headers = config.get('headers', [])
                for col_idx, header in enumerate(headers, 1):
                    cell = ws.cell(row=1, column=col_idx, value=header)
                    # Format header cells
                    cell.font = Font(bold=True, color="FFFFFF")
                    cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                
                # Add default data if provided
                default_data = config.get('default_data', [])
                for row_idx, row_data in enumerate(default_data, 2):
                    if isinstance(row_data, dict):
                        # Map dictionary data to columns
                        for col_idx, header in enumerate(headers, 1):
                            # Convert header to snake_case key for lookup
                            key = header.lower().replace(' ', '_')
                            value = row_data.get(key, '')
                            ws.cell(row=row_idx, column=col_idx, value=value)
                    elif isinstance(row_data, list):
                        # Direct list data
                        for col_idx, value in enumerate(row_data, 1):
                            if col_idx <= len(headers):
                                ws.cell(row=row_idx, column=col_idx, value=value)
                
                # Auto-adjust column widths
                for column in ws.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    ws.column_dimensions[column_letter].width = max(adjusted_width, 12)
                
                # Create table formatting if there's data
                if len(headers) > 0:
                    last_row = max(2, len(default_data) + 1)
                    last_col = len(headers)
                    table_range = f"A1:{ws.cell(row=last_row, column=last_col).coordinate}"
                    
                    table = Table(displayName=f"Table_{sheet_name}", ref=table_range)
                    style = TableStyleInfo(
                        name="TableStyleMedium2",
                        showFirstColumn=False,
                        showLastColumn=False,
                        showRowStripes=True,
                        showColumnStripes=False
                    )
                    table.tableStyleInfo = style
                    ws.add_table(table)
            
            # Save workbook
            wb.save(file_path)
            return True
            
        except Exception as e:
            print(f"Error creating Excel workbook: {str(e)}")
            return False
    
    @staticmethod
    def read_sheet_data(file_path: str, sheet_name: str) -> pd.DataFrame:
        """
        Read data from Excel sheet.
        
        Args:
            file_path: Path to Excel file
            sheet_name: Name of sheet to read
            
        Returns:
            pd.DataFrame: Sheet data as DataFrame
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Excel file not found: {file_path}")
                
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            return df
            
        except Exception as e:
            print(f"Error reading Excel sheet: {str(e)}")
            return pd.DataFrame()
    
    @staticmethod
    def write_sheet_data(file_path: str, sheet_name: str, data: pd.DataFrame) -> bool:
        """
        Write data to Excel sheet.
        
        Args:
            file_path: Path to Excel file
            sheet_name: Name of sheet to write
            data: DataFrame to write
            
        Returns:
            bool: True if write successful
        """
        try:
            # Read existing workbook if it exists
            if os.path.exists(file_path):
                with pd.ExcelWriter(file_path, mode='a', if_sheet_exists='replace', engine='openpyxl') as writer:
                    data.to_excel(writer, sheet_name=sheet_name, index=False)
            else:
                # Create new workbook
                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    data.to_excel(writer, sheet_name=sheet_name, index=False)
                    
            return True
            
        except Exception as e:
            print(f"Error writing Excel sheet: {str(e)}")
            return False
    
    @staticmethod
    def validate_sheet_structure(file_path: str, sheet_name: str, expected_headers: list) -> bool:
        """
        Validate sheet has expected structure.
        
        Args:
            file_path: Path to Excel file
            sheet_name: Name of sheet to validate
            expected_headers: List of expected header names
            
        Returns:
            bool: True if structure is valid
        """
        try:
            df = ExcelUtils.read_sheet_data(file_path, sheet_name)
            
            if df.empty:
                return False
                
            # Check if all expected headers are present
            actual_headers = df.columns.tolist()
            
            for expected_header in expected_headers:
                if expected_header not in actual_headers:
                    return False
                    
            return True
            
        except Exception as e:
            print(f"Error validating Excel sheet: {str(e)}")
            return False
    
    @staticmethod
    def get_sheet_names(file_path: str) -> list:
        """
        Get list of sheet names in Excel file.
        
        Args:
            file_path: Path to Excel file
            
        Returns:
            list: List of sheet names
        """
        try:
            if not os.path.exists(file_path):
                return []
                
            xl_file = pd.ExcelFile(file_path)
            return xl_file.sheet_names
            
        except Exception as e:
            print(f"Error getting sheet names: {str(e)}")
            return []
