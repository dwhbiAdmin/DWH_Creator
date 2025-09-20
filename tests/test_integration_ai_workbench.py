"""
Integration Tests for AI Workbench Manager
==========================================

Tests for the AIWorkbenchManager class that integrates AI features with workbook operations.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pandas as pd

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from backend.ai_workbench_manager import AIWorkbenchManager


class TestAIWorkbenchManagerIntegration:
    """Integration test cases for AIWorkbenchManager."""
    
    @pytest.fixture
    def ai_workbench_manager(self, sample_workbook_path):
        """Create AIWorkbenchManager with sample workbook."""
        return AIWorkbenchManager(str(sample_workbook_path), "test_api_key")
    
    @pytest.fixture
    def mock_successful_ai(self):
        """Mock successful AI responses."""
        with patch.object(AIWorkbenchManager, 'is_ai_available', return_value=True), \
             patch('utils.ai_comment_generator.AICommentGenerator') as mock_ai:
            mock_ai.return_value.is_available.return_value = True
            mock_ai.return_value.generate_artifact_comment.return_value = "Generated artifact comment"
            mock_ai.return_value.generate_column_comment.return_value = "Generated column comment"
            mock_ai.return_value.generate_readable_column_name.return_value = "generated_column_name"
            yield mock_ai
    
    @pytest.fixture
    def mock_unavailable_ai(self):
        """Mock unavailable AI."""
        with patch.object(AIWorkbenchManager, 'is_ai_available', return_value=False):
            yield
    
    def test_initialization(self, ai_workbench_manager):
        """Test AIWorkbenchManager initializes correctly."""
        assert ai_workbench_manager.workbook_path is not None
        assert hasattr(ai_workbench_manager, 'ai_generator')
        assert hasattr(ai_workbench_manager, 'excel_utils')
        assert hasattr(ai_workbench_manager, 'logger')
    
    @pytest.mark.integration
    def test_is_ai_available(self, ai_workbench_manager, mock_successful_ai):
        """Test AI availability check."""
        assert ai_workbench_manager.is_ai_available() is True
    
    @pytest.mark.integration
    def test_is_ai_unavailable(self, ai_workbench_manager, mock_unavailable_ai):
        """Test AI unavailable scenario."""
        assert ai_workbench_manager.is_ai_available() is False
    
    @pytest.mark.integration
    @patch('utils.excel_utils.ExcelUtils.read_sheet_data')
    @patch('utils.excel_utils.ExcelUtils.write_sheet_data')
    def test_generate_artifact_comments_success(self, mock_write, mock_read, ai_workbench_manager, mock_successful_ai):
        """Test successful artifact comment generation."""
        # Setup mock data
        mock_artifacts_df = pd.DataFrame({
            'Artifact Name': ['customers_bronze', 'orders_bronze'],
            'Stage Name': ['bronze', 'bronze'],
            'Artifact Comment': ['', '']  # Empty comments to trigger generation
        })
        mock_read.return_value = mock_artifacts_df
        mock_write.return_value = True
        
        result = ai_workbench_manager.generate_artifact_comments()
        
        assert result is True
        mock_read.assert_called_once_with(ai_workbench_manager.workbook_path, "Artifacts")
        mock_write.assert_called_once()
    
    @pytest.mark.integration
    @patch('utils.excel_utils.ExcelUtils.read_sheet_data')
    def test_generate_artifact_comments_no_data(self, mock_read, ai_workbench_manager, mock_successful_ai):
        """Test artifact comment generation with no data."""
        mock_read.return_value = pd.DataFrame()  # Empty DataFrame
        
        result = ai_workbench_manager.generate_artifact_comments()
        
        assert result is True  # Should succeed but do nothing
        mock_read.assert_called_once()
    
    @pytest.mark.integration
    @patch('utils.excel_utils.ExcelUtils.read_sheet_data')
    def test_generate_artifact_comments_already_have_comments(self, mock_read, ai_workbench_manager, mock_successful_ai):
        """Test artifact comment generation when comments already exist."""
        # Setup mock data with existing comments
        mock_artifacts_df = pd.DataFrame({
            'Artifact Name': ['customers_bronze', 'orders_bronze'],
            'Stage Name': ['bronze', 'bronze'],
            'Artifact Comment': ['Existing comment 1', 'Existing comment 2']
        })
        mock_read.return_value = mock_artifacts_df
        
        result = ai_workbench_manager.generate_artifact_comments()
        
        assert result is True
        mock_read.assert_called_once()
    
    @pytest.mark.integration
    @patch('utils.excel_utils.ExcelUtils.read_sheet_data')
    @patch('utils.excel_utils.ExcelUtils.write_sheet_data')
    def test_generate_column_comments_success(self, mock_write, mock_read, ai_workbench_manager, mock_successful_ai):
        """Test successful column comment generation."""
        # Setup mock data
        mock_columns_df = pd.DataFrame({
            'Column Name': ['customer_id', 'first_name'],
            'Data Type': ['INT', 'VARCHAR(50)'],
            'Artifact ID': [1, 1],
            'Column Comment': ['', '']  # Empty comments to trigger generation
        })
        mock_read.return_value = mock_columns_df
        mock_write.return_value = True
        
        result = ai_workbench_manager.generate_column_comments()
        
        assert result is True
        mock_read.assert_called_once_with(ai_workbench_manager.workbook_path, "Columns")
        mock_write.assert_called_once()
    
    @pytest.mark.integration
    @patch('utils.excel_utils.ExcelUtils.read_sheet_data')
    @patch('utils.excel_utils.ExcelUtils.write_sheet_data')
    def test_generate_readable_column_names_success(self, mock_write, mock_read, ai_workbench_manager, mock_successful_ai):
        """Test successful readable column name generation."""
        # Setup mock data
        mock_columns_df = pd.DataFrame({
            'Column Name': ['cust_id', 'fname'],
            'Data Type': ['INT', 'VARCHAR(50)'],
            'Column Business Name': ['', '']  # Empty names to trigger generation
        })
        mock_read.return_value = mock_columns_df
        mock_write.return_value = True
        
        result = ai_workbench_manager.generate_readable_column_names()
        
        assert result is True
        mock_read.assert_called_once_with(ai_workbench_manager.workbook_path, "Columns")
        mock_write.assert_called_once()
    
    @pytest.mark.integration
    def test_generate_all_ai_comments_unavailable(self, ai_workbench_manager, mock_unavailable_ai):
        """Test generate_all_ai_comments when AI is unavailable."""
        result = ai_workbench_manager.generate_all_ai_comments()
        assert result is False
    
    @pytest.mark.integration
    @patch('utils.excel_utils.ExcelUtils.read_sheet_data')
    @patch('utils.excel_utils.ExcelUtils.write_sheet_data')
    def test_generate_all_ai_comments_success(self, mock_write, mock_read, ai_workbench_manager, mock_successful_ai):
        """Test successful generation of all AI comments."""
        # Setup mock data for both artifacts and columns
        mock_artifacts_df = pd.DataFrame({
            'Artifact Name': ['customers_bronze'],
            'Stage Name': ['bronze'],
            'Artifact Comment': ['']
        })
        
        mock_columns_df = pd.DataFrame({
            'Column Name': ['customer_id'],
            'Data Type': ['INT'],
            'Artifact ID': [1],
            'Column Comment': ['']
        })
        
        # Configure mock to return different data based on sheet name
        def mock_read_side_effect(workbook_path, sheet_name):
            if sheet_name == "Artifacts":
                return mock_artifacts_df
            elif sheet_name == "Columns":
                return mock_columns_df
            return pd.DataFrame()
        
        mock_read.side_effect = mock_read_side_effect
        mock_write.return_value = True
        
        result = ai_workbench_manager.generate_all_ai_comments()
        
        assert result is True
        assert mock_read.call_count == 2  # Called for both Artifacts and Columns
        assert mock_write.call_count == 2  # Written back for both sheets
    
    @pytest.mark.integration
    @patch('utils.excel_utils.ExcelUtils.read_sheet_data')
    def test_error_handling_read_failure(self, mock_read, ai_workbench_manager, mock_successful_ai):
        """Test error handling when Excel read fails."""
        mock_read.side_effect = Exception("Excel read error")
        
        result = ai_workbench_manager.generate_artifact_comments()
        
        assert result is False
    
    @pytest.mark.integration
    @patch('utils.excel_utils.ExcelUtils.read_sheet_data')
    @patch('utils.excel_utils.ExcelUtils.write_sheet_data')
    def test_error_handling_write_failure(self, mock_write, mock_read, ai_workbench_manager, mock_successful_ai):
        """Test error handling when Excel write fails."""
        # Setup successful read but failed write
        mock_artifacts_df = pd.DataFrame({
            'Artifact Name': ['customers_bronze'],
            'Stage Name': ['bronze'],
            'Artifact Comment': ['']
        })
        mock_read.return_value = mock_artifacts_df
        mock_write.return_value = False
        
        result = ai_workbench_manager.generate_artifact_comments()
        
        assert result is False
    
    @pytest.mark.integration
    @patch('utils.excel_utils.ExcelUtils.read_sheet_data')
    @patch('utils.excel_utils.ExcelUtils.write_sheet_data')
    def test_partial_ai_generation_success(self, mock_write, mock_read, ai_workbench_manager):
        """Test partial success in AI generation."""
        # Mock AI that sometimes fails
        with patch('utils.ai_comment_generator.AICommentGenerator') as mock_ai:
            mock_ai.return_value.is_available.return_value = True
            # First call succeeds, second call fails
            mock_ai.return_value.generate_artifact_comment.side_effect = ["Success comment", ""]
            
            mock_artifacts_df = pd.DataFrame({
                'Artifact Name': ['customers_bronze', 'orders_bronze'],
                'Stage Name': ['bronze', 'bronze'],
                'Artifact Comment': ['', '']
            })
            mock_read.return_value = mock_artifacts_df
            mock_write.return_value = True
            
            result = ai_workbench_manager.generate_artifact_comments()
            
            # Should still succeed even with partial failures
            assert result is True
    
    @pytest.mark.integration
    @patch('utils.excel_utils.ExcelUtils.read_sheet_data')
    def test_mixed_existing_and_new_comments(self, mock_read, ai_workbench_manager, mock_successful_ai):
        """Test handling of mixed existing and new comments."""
        mock_artifacts_df = pd.DataFrame({
            'Artifact Name': ['customers_bronze', 'orders_bronze', 'products_bronze'],
            'Stage Name': ['bronze', 'bronze', 'bronze'],
            'Artifact Comment': ['Existing comment', '', 'Another existing comment']
        })
        mock_read.return_value = mock_artifacts_df
        
        with patch('utils.excel_utils.ExcelUtils.write_sheet_data') as mock_write:
            mock_write.return_value = True
            
            result = ai_workbench_manager.generate_artifact_comments()
            
            assert result is True
            # Should only generate comment for the one without existing comment
            mock_write.assert_called_once()
    
    @pytest.mark.integration
    def test_workbook_path_handling(self, temp_dir):
        """Test handling of different workbook path scenarios."""
        # Test with non-existent workbook
        non_existent_path = temp_dir / "non_existent.xlsx"
        ai_manager = AIWorkbenchManager(str(non_existent_path), "test_key")
        
        with patch('utils.ai_comment_generator.AICommentGenerator') as mock_ai:
            mock_ai.return_value.is_available.return_value = True
            
            # Should handle gracefully when workbook doesn't exist
            result = ai_manager.generate_artifact_comments()
            assert result is True  # Excel utils should return empty DataFrame for non-existent file
