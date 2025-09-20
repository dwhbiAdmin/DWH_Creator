"""
Test Readable Column Names Generation
=====================================

Tests for AI-powered human-readable column name generation functionality.

This module tests the ability to generate business-friendly column names
from technical source column names using AI.
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pandas as pd

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from backend.ai_workbench_manager import AIWorkbenchManager
from backend.workbench_manager import WorkbenchManager


class TestReadableColumnNames(unittest.TestCase):
    """Test cases for readable column names generation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_project_path = Path("test_project")
        self.test_workbook_path = self.test_project_path / "data" / "test_workbook.xlsx"
        self.api_key = "test_api_key"
        
        # Create AI workbench manager with proper workbook path
        self.ai_workbench = AIWorkbenchManager(str(self.test_workbook_path), self.api_key)
        
    def test_ai_workbench_manager_initialization(self):
        """Test AI workbench manager initializes correctly."""
        self.assertEqual(self.ai_workbench.workbook_path, str(self.test_workbook_path))
        # Check that AI generator was created 
        self.assertIsNotNone(self.ai_workbench.ai_generator)
        self.assertIsNotNone(self.ai_workbench.logger)
        
    @patch('utils.excel_utils.pd.read_excel')
    @patch('utils.excel_utils.openpyxl.load_workbook')
    def test_generate_readable_column_names_success(self, mock_load_workbook, mock_read_excel):
        """Test successful generation of readable column names."""
        # Mock Excel data
        mock_df = pd.DataFrame({
            'Column Name': ['customer_id', 'order_dt', 'product_sku', 'total_amt'],
            'Source Column': ['CUST_ID', 'ORDER_DATE', 'PROD_SKU', 'TOTAL_AMOUNT'],
            'Readable Column Name': ['', '', '', '']  # Empty initially
        })
        mock_read_excel.return_value = mock_df
        
        # Mock workbook operations
        mock_workbook = Mock()
        mock_worksheet = Mock()
        mock_workbook.__getitem__.return_value = mock_worksheet
        mock_load_workbook.return_value = mock_workbook
        
        # Mock AI generator
        with patch.object(self.ai_workbench, 'ai_generator') as mock_ai:
            mock_ai.generate_readable_column_name.side_effect = [
                "Customer ID",
                "Order Date", 
                "Product SKU",
                "Total Amount"
            ]
            
            # Test generation
            result = self.ai_workbench.generate_readable_column_names()
            
            # Verify results
            self.assertTrue(result)
            self.assertEqual(mock_ai.generate_readable_column_name.call_count, 4)
            
    @patch('utils.excel_utils.pd.read_excel')
    def test_generate_readable_column_names_no_columns(self, mock_read_excel):
        """Test handling when no columns exist."""
        # Mock empty data
        mock_df = pd.DataFrame(columns=['Column Name', 'Source Column', 'Readable Column Name'])
        mock_read_excel.return_value = mock_df
        
        result = self.ai_workbench.generate_readable_column_names()
        
        # Should still succeed but do nothing
        self.assertTrue(result)
        
    @patch('utils.excel_utils.pd.read_excel')
    def test_generate_readable_column_names_file_error(self, mock_read_excel):
        """Test handling of file read errors."""
        mock_read_excel.side_effect = FileNotFoundError("Workbook not found")
        
        result = self.ai_workbench.generate_readable_column_names()
        
        self.assertFalse(result)
        
    @patch('utils.excel_utils.pd.read_excel')
    @patch('utils.excel_utils.openpyxl.load_workbook')
    def test_generate_readable_column_names_ai_error(self, mock_load_workbook, mock_read_excel):
        """Test handling of AI generation errors."""
        # Mock Excel data
        mock_df = pd.DataFrame({
            'Column Name': ['customer_id'],
            'Source Column': ['CUST_ID'],
            'Readable Column Name': ['']
        })
        mock_read_excel.return_value = mock_df
        
        # Mock workbook operations
        mock_workbook = Mock()
        mock_worksheet = Mock()
        mock_workbook.__getitem__.return_value = mock_worksheet
        mock_load_workbook.return_value = mock_workbook
        
        # Mock AI generator with error
        with patch.object(self.ai_workbench, 'ai_generator') as mock_ai:
            mock_ai.generate_readable_column_name.side_effect = Exception("AI API Error")
            
            result = self.ai_workbench.generate_readable_column_names()
            
            # Should handle error gracefully
            self.assertFalse(result)
            
    def test_workbench_manager_integration(self):
        """Test integration with workbench manager."""
        # Create workbench manager with mock AI
        with patch('backend.workbench_manager.AIWorkbenchManager') as mock_ai_class:
            mock_ai_instance = Mock()
            mock_ai_instance.generate_readable_column_names.return_value = True
            mock_ai_class.return_value = mock_ai_instance
            
            workbench = WorkbenchManager(self.test_project_path, self.api_key)
            
            # Test method exists and calls AI workbench
            result = workbench.generate_readable_column_names()
            
            self.assertTrue(result)
            mock_ai_instance.generate_readable_column_names.assert_called_once()
            
    def test_workbench_manager_no_ai(self):
        """Test workbench manager without AI initialization."""
        workbench = WorkbenchManager(self.test_project_path, None)
        
        result = workbench.generate_readable_column_names()
        
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
