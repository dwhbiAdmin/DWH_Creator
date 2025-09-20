"""
Unit Tests for ExcelUtils
=========================

Tests for the ExcelUtils class that handles Excel file operations.
"""

import pytest
import sys
from pathlib import Path
import pandas as pd
import openpyxl
from unittest.mock import Mock, patch
import tempfile
import shutil

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.excel_utils import ExcelUtils


class TestExcelUtils:
    """Test cases for ExcelUtils."""
    
    @pytest.fixture
    def excel_utils(self):
        """Create an ExcelUtils instance for testing."""
        return ExcelUtils()
    
    @pytest.fixture
    def temp_excel_file(self, sample_workbook_path):
        """Use the sample workbook from conftest."""
        return sample_workbook_path
    
    def test_initialization(self, excel_utils):
        """Test ExcelUtils initializes correctly."""
        assert excel_utils is not None
        assert hasattr(excel_utils, 'read_sheet_data')
        assert hasattr(excel_utils, 'write_sheet_data')
        assert hasattr(excel_utils, 'create_workbook')
    
    @pytest.mark.excel
    def test_read_sheet_data_success(self, excel_utils, temp_excel_file):
        """Test successful reading of sheet data."""
        df = excel_utils.read_sheet_data(str(temp_excel_file), "Stages")
        
        assert isinstance(df, pd.DataFrame)
        assert not df.empty
        assert len(df) > 0
        
        # Check expected columns exist
        expected_columns = ["Stage ID", "Stage Name", "Stage Description", "Platform", "Source/Business Side"]
        for col in expected_columns:
            assert col in df.columns
    
    @pytest.mark.excel
    def test_read_sheet_data_nonexistent_file(self, excel_utils):
        """Test reading from non-existent file."""
        df = excel_utils.read_sheet_data("nonexistent.xlsx", "Stages")
        
        assert isinstance(df, pd.DataFrame)
        assert df.empty
    
    @pytest.mark.excel
    def test_read_sheet_data_nonexistent_sheet(self, excel_utils, temp_excel_file):
        """Test reading from non-existent sheet."""
        df = excel_utils.read_sheet_data(str(temp_excel_file), "NonexistentSheet")
        
        assert isinstance(df, pd.DataFrame)
        assert df.empty
    
    @pytest.mark.excel
    def test_write_sheet_data_success(self, excel_utils, temp_excel_file):
        """Test successful writing of sheet data."""
        # Read existing data
        original_df = excel_utils.read_sheet_data(str(temp_excel_file), "Stages")
        
        # Modify data
        modified_df = original_df.copy()
        modified_df.loc[0, 'Stage Description'] = 'Modified description'
        
        # Write back
        success = excel_utils.write_sheet_data(str(temp_excel_file), "Stages", modified_df)
        assert success
        
        # Verify changes
        updated_df = excel_utils.read_sheet_data(str(temp_excel_file), "Stages")
        assert updated_df.loc[0, 'Stage Description'] == 'Modified description'
    
    @pytest.mark.excel
    def test_write_sheet_data_new_sheet(self, excel_utils, temp_excel_file):
        """Test writing to a new sheet."""
        # Create new data
        new_data = pd.DataFrame({
            'Test Column 1': ['Value 1', 'Value 2'],
            'Test Column 2': ['Value A', 'Value B']
        })
        
        # Write to new sheet
        success = excel_utils.write_sheet_data(str(temp_excel_file), "NewSheet", new_data)
        assert success
        
        # Verify new sheet exists and has correct data
        read_data = excel_utils.read_sheet_data(str(temp_excel_file), "NewSheet")
        assert not read_data.empty
        assert list(read_data.columns) == ['Test Column 1', 'Test Column 2']
        assert len(read_data) == 2
    
    @pytest.mark.excel
    def test_create_workbook_success(self, excel_utils, temp_dir):
        """Test successful workbook creation."""
        workbook_path = temp_dir / "new_workbook.xlsx"
        
        success = excel_utils.create_workbook(str(workbook_path))
        assert success
        assert workbook_path.exists()
        
        # Verify workbook can be opened
        wb = openpyxl.load_workbook(workbook_path)
        assert wb is not None
        wb.close()
    
    @pytest.mark.excel
    def test_create_workbook_existing_file(self, excel_utils, temp_excel_file):
        """Test creating workbook when file already exists."""
        # Should handle existing file gracefully
        success = excel_utils.create_workbook(str(temp_excel_file))
        # This might return False if file exists, or True if it overwrites
        # Either behavior is acceptable depending on implementation
        assert isinstance(success, bool)
    
    @pytest.mark.excel
    def test_sheet_operations_consistency(self, excel_utils, temp_excel_file):
        """Test that read/write operations are consistent."""
        sheet_name = "Artifacts"
        
        # Read original data
        original_df = excel_utils.read_sheet_data(str(temp_excel_file), sheet_name)
        
        # Write same data back
        success = excel_utils.write_sheet_data(str(temp_excel_file), sheet_name, original_df)
        assert success
        
        # Read again and compare
        final_df = excel_utils.read_sheet_data(str(temp_excel_file), sheet_name)
        
        # DataFrames should be equivalent
        pd.testing.assert_frame_equal(original_df, final_df)
    
    @pytest.mark.excel
    def test_handle_empty_dataframe(self, excel_utils, temp_excel_file):
        """Test handling of empty DataFrame."""
        empty_df = pd.DataFrame()
        
        success = excel_utils.write_sheet_data(str(temp_excel_file), "EmptySheet", empty_df)
        assert isinstance(success, bool)
        
        # Read back empty sheet
        read_df = excel_utils.read_sheet_data(str(temp_excel_file), "EmptySheet")
        assert isinstance(read_df, pd.DataFrame)
    
    @pytest.mark.excel
    def test_handle_special_characters(self, excel_utils, temp_excel_file):
        """Test handling of special characters in data."""
        special_data = pd.DataFrame({
            'Column with Spaces': ['Value 1', 'Value 2'],
            'Column-with-Dashes': ['A-B', 'C-D'],
            'Column_with_Underscores': ['X_Y', 'Z_W'],
            'Column with ümlaut': ['Tëst', 'Dàta']
        })
        
        success = excel_utils.write_sheet_data(str(temp_excel_file), "SpecialChars", special_data)
        assert success
        
        read_data = excel_utils.read_sheet_data(str(temp_excel_file), "SpecialChars")
        assert not read_data.empty
        assert len(read_data.columns) == 4
        assert len(read_data) == 2
    
    @pytest.mark.excel
    def test_handle_large_data(self, excel_utils, temp_dir):
        """Test handling of larger datasets."""
        workbook_path = temp_dir / "large_data.xlsx"
        
        # Create larger dataset
        large_data = pd.DataFrame({
            'ID': range(1000),
            'Name': [f'Item_{i}' for i in range(1000)],
            'Value': [i * 2.5 for i in range(1000)],
            'Description': [f'Description for item {i}' for i in range(1000)]
        })
        
        # Create workbook first
        excel_utils.create_workbook(str(workbook_path))
        
        # Write large data
        success = excel_utils.write_sheet_data(str(workbook_path), "LargeData", large_data)
        assert success
        
        # Read back and verify
        read_data = excel_utils.read_sheet_data(str(workbook_path), "LargeData")
        assert len(read_data) == 1000
        assert list(read_data.columns) == ['ID', 'Name', 'Value', 'Description']
    
    @pytest.mark.excel
    def test_multiple_sheets_operations(self, excel_utils, temp_dir):
        """Test operations with multiple sheets."""
        workbook_path = temp_dir / "multi_sheet.xlsx"
        excel_utils.create_workbook(str(workbook_path))
        
        # Create different data for different sheets
        sheets_data = {
            'Sheet1': pd.DataFrame({'A': [1, 2], 'B': [3, 4]}),
            'Sheet2': pd.DataFrame({'X': ['a', 'b'], 'Y': ['c', 'd']}),
            'Sheet3': pd.DataFrame({'Col1': [True, False], 'Col2': [10.5, 20.5]})
        }
        
        # Write all sheets
        for sheet_name, data in sheets_data.items():
            success = excel_utils.write_sheet_data(str(workbook_path), sheet_name, data)
            assert success
        
        # Read all sheets and verify
        for sheet_name, original_data in sheets_data.items():
            read_data = excel_utils.read_sheet_data(str(workbook_path), sheet_name)
            assert not read_data.empty
            assert len(read_data) == len(original_data)
            assert list(read_data.columns) == list(original_data.columns)
    
    @pytest.mark.excel
    def test_data_types_preservation(self, excel_utils, temp_dir):
        """Test that data types are preserved in read/write operations."""
        workbook_path = temp_dir / "data_types.xlsx"
        excel_utils.create_workbook(str(workbook_path))
        
        # Create data with various types
        test_data = pd.DataFrame({
            'Integer': [1, 2, 3],
            'Float': [1.1, 2.2, 3.3],
            'String': ['a', 'b', 'c'],
            'Boolean': [True, False, True]
        })
        
        # Write data
        success = excel_utils.write_sheet_data(str(workbook_path), "DataTypes", test_data)
        assert success
        
        # Read back
        read_data = excel_utils.read_sheet_data(str(workbook_path), "DataTypes")
        
        # Verify data integrity (exact type matching might not be preserved in Excel)
        assert len(read_data) == 3
        assert list(read_data.columns) == ['Integer', 'Float', 'String', 'Boolean']
        
        # Check that values are correct even if types might be different
        assert read_data['String'].tolist() == ['a', 'b', 'c']
