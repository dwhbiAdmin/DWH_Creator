"""
Test Suite for Column Cascading Engine
======================================

Tests for the column cascading functionality including:
- Cascading engine initialization
- Data type mappings
- Technical columns configuration
- All upstream relation types (main, get_key, lookup, pbi)
- Integration with workbench manager
"""

import pytest
import pandas as pd
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add src to path for imports
import sys
current_dir = Path(__file__).parent
src_dir = current_dir.parent / "src"
sys.path.insert(0, str(src_dir))

from utils.column_cascading import ColumnCascadingEngine, UpstreamRelationType
from utils.cascading_config_setup import CascadingConfigManager
from backend.workbench_manager import WorkbenchManager

class TestColumnCascadingEngine:
    """Test the column cascading engine functionality."""
    
    @pytest.fixture
    def temp_workbook(self):
        """Create a temporary workbook for testing."""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as temp_file:
            temp_path = temp_file.name
            
            # Create test data
            stages_data = pd.DataFrame([
                {"Stage Name": "bronze", "Platform": "SQL Server", "Source or Business Side": "source"},
                {"Stage Name": "silver", "Platform": "Databricks", "Source or Business Side": "business"},
                {"Stage Name": "gold", "Platform": "Power BI", "Source or Business Side": "business"}
            ])
            
            artifacts_data = pd.DataFrame([
                {"Artifact ID": 1, "Artifact Name": "raw_sales", "Stage Name": "bronze", "Upstream Relation": "", "Upstream Artifact": ""},
                {"Artifact ID": 2, "Artifact Name": "clean_sales", "Stage Name": "silver", "Upstream Relation": "main", "Upstream Artifact": "1"},
                {"Artifact ID": 3, "Artifact Name": "dim_customer", "Stage Name": "silver", "Upstream Relation": "main", "Upstream Artifact": "1"},
                {"Artifact ID": 4, "Artifact Name": "fact_sales", "Stage Name": "gold", "Upstream Relation": "get_key", "Upstream Artifact": "2,3"},
                {"Artifact ID": 5, "Artifact Name": "lookup_product", "Stage Name": "gold", "Upstream Relation": "lookup", "Upstream Artifact": "2"},
                {"Artifact ID": 6, "Artifact Name": "pbi_dashboard", "Stage Name": "gold", "Upstream Relation": "pbi", "Upstream Artifact": "4"}
            ])
            
            columns_data = pd.DataFrame([
                {"Column ID": 1, "Column Name": "sale_id", "Artifact ID": 1, "Data Type": "INT", "Order": 1},
                {"Column ID": 2, "Column Name": "customer_id", "Artifact ID": 1, "Data Type": "INT", "Order": 2},
                {"Column ID": 3, "Column Name": "sale_date", "Artifact ID": 1, "Data Type": "DATETIME", "Order": 3},
                {"Column ID": 4, "Column Name": "amount", "Artifact ID": 1, "Data Type": "DECIMAL", "Order": 4}
            ])
            
            # Write to Excel
            with pd.ExcelWriter(temp_path, engine='openpyxl') as writer:
                stages_data.to_excel(writer, sheet_name='Stages', index=False)
                artifacts_data.to_excel(writer, sheet_name='Artifacts', index=False)
                columns_data.to_excel(writer, sheet_name='Columns', index=False)
            
            yield temp_path
            
            # Cleanup
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    @pytest.fixture
    def temp_config(self):
        """Create a temporary config file for testing."""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as temp_file:
            temp_path = temp_file.name
            
            config_manager = CascadingConfigManager()
            config_manager.create_default_config_file(temp_path)
            
            yield temp_path
            
            # Cleanup
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    @pytest.fixture
    def cascading_engine(self, temp_workbook, temp_config):
        """Create a cascading engine instance for testing."""
        return ColumnCascadingEngine(temp_workbook, temp_config)
    
    def test_engine_initialization(self, cascading_engine):
        """Test that the engine initializes correctly."""
        assert cascading_engine.workbook_path is not None
        assert cascading_engine.config_path is not None
        assert cascading_engine.excel_utils is not None
        assert cascading_engine.logger is not None
    
    def test_data_type_mappings_loading(self, cascading_engine):
        """Test that data type mappings are loaded correctly."""
        assert not cascading_engine.data_type_mappings.empty
        assert 'SQL Server Data Type' in cascading_engine.data_type_mappings.columns
        assert 'Databricks SQL Data Type' in cascading_engine.data_type_mappings.columns
        assert 'Power BI Data Type' in cascading_engine.data_type_mappings.columns
    
    def test_technical_columns_loading(self, cascading_engine):
        """Test that technical columns configuration is loaded correctly."""
        assert 'bronze' in cascading_engine.technical_columns
        assert 'silver' in cascading_engine.technical_columns
        assert 'gold' in cascading_engine.technical_columns
        
        # Check bronze stage has required technical columns
        bronze_cols = cascading_engine.technical_columns['bronze']
        bronze_col_names = [col['column_name'] for col in bronze_cols]
        assert '__SourceSystem' in bronze_col_names
        assert '__bronze_insertDT' in bronze_col_names
    
    def test_data_type_conversion(self, cascading_engine):
        """Test data type conversion between platforms."""
        # Test SQL Server to Databricks conversion
        converted = cascading_engine._convert_data_type('VARCHAR', 'SQL Server', 'Databricks')
        assert converted == 'STRING'
        
        # Test SQL Server to Power BI conversion
        converted = cascading_engine._convert_data_type('INT', 'SQL Server', 'Power BI')
        assert converted == 'Whole Number'
        
        # Test same platform (no conversion)
        converted = cascading_engine._convert_data_type('INT', 'SQL Server', 'SQL Server')
        assert converted == 'INT'
    
    @patch.object(ColumnCascadingEngine, '_get_next_column_id')
    @patch.object(ColumnCascadingEngine, '_get_next_column_order')
    def test_main_relation_cascading(self, mock_order, mock_id, cascading_engine):
        """Test cascading for 'main' upstream relationship."""
        mock_id.return_value = 100
        mock_order.return_value = 10
        
        # Mock required methods for testing
        with patch.object(cascading_engine.excel_utils, 'read_sheet_data') as mock_read:
            with patch.object(cascading_engine.excel_utils, 'write_sheet_data') as mock_write:
                # Setup mock data
                artifacts_df = pd.DataFrame([
                    {"Artifact ID": 2, "Artifact Name": "clean_sales", "Stage Name": "silver", "Upstream Relation": "main", "Upstream Artifact": "1"}
                ])
                
                stages_df = pd.DataFrame([
                    {"Stage Name": "silver", "Platform": "Databricks", "Source or Business Side": "business"}
                ])
                
                columns_df = pd.DataFrame([
                    {"Column ID": 1, "Column Name": "sale_id", "Artifact ID": 1, "Data Type": "INT"},
                    {"Column ID": 2, "Column Name": "customer_id", "Artifact ID": 1, "Data Type": "INT"}
                ])
                
                mock_read.side_effect = lambda path, sheet: {
                    'Artifacts': artifacts_df,
                    'Stages': stages_df,
                    'Columns': columns_df
                }[sheet]
                
                mock_write.return_value = True
                
                # Test cascading
                result = cascading_engine.cascade_columns_for_artifact(2)
                assert result is True
                mock_write.assert_called_once()
    
    def test_get_key_relation_cascading(self, cascading_engine):
        """Test cascading for 'get_key' upstream relationship."""
        # Mock the gold stage artifact
        with patch.object(cascading_engine.excel_utils, 'read_sheet_data') as mock_read:
            artifacts_df = pd.DataFrame([
                {"Artifact ID": 4, "Artifact Name": "fact_sales", "Stage Name": "gold", "Upstream Relation": "get_key", "Upstream Artifact": "2,3"}
            ])
            
            stages_df = pd.DataFrame([
                {"Stage Name": "gold", "Platform": "Power BI", "Source or Business Side": "business"}
            ])
            
            mock_read.side_effect = lambda path, sheet: {
                'Artifacts': artifacts_df,
                'Stages': stages_df,
                'Columns': pd.DataFrame()
            }[sheet]
            
            # Test that get_key relation is handled
            target_artifact = artifacts_df.iloc[0]
            relation_type = UpstreamRelationType.GET_KEY
            
            result = cascading_engine._cascade_by_relation_type(
                target_artifact, artifacts_df, pd.DataFrame(), stages_df, relation_type
            )
            
            # Should return a list (even if empty due to mocking)
            assert isinstance(result, list)
    
    def test_lookup_relation_cascading(self, cascading_engine):
        """Test cascading for 'lookup' upstream relationship."""
        with patch.object(cascading_engine.excel_utils, 'read_sheet_data') as mock_read:
            artifacts_df = pd.DataFrame([
                {"Artifact ID": 5, "Artifact Name": "lookup_product", "Stage Name": "gold", "Upstream Relation": "lookup", "Upstream Artifact": "2"}
            ])
            
            stages_df = pd.DataFrame([
                {"Stage Name": "gold", "Platform": "Power BI", "Source or Business Side": "business"}
            ])
            
            mock_read.side_effect = lambda path, sheet: {
                'Artifacts': artifacts_df,
                'Stages': stages_df,
                'Columns': pd.DataFrame()
            }[sheet]
            
            target_artifact = artifacts_df.iloc[0]
            relation_type = UpstreamRelationType.LOOKUP
            
            result = cascading_engine._cascade_by_relation_type(
                target_artifact, artifacts_df, pd.DataFrame(), stages_df, relation_type
            )
            
            assert isinstance(result, list)
    
    def test_pbi_relation_cascading(self, cascading_engine):
        """Test cascading for 'pbi' upstream relationship (should have no impact)."""
        with patch.object(cascading_engine.excel_utils, 'read_sheet_data') as mock_read:
            artifacts_df = pd.DataFrame([
                {"Artifact ID": 6, "Artifact Name": "pbi_dashboard", "Stage Name": "gold", "Upstream Relation": "pbi", "Upstream Artifact": "4"}
            ])
            
            stages_df = pd.DataFrame([
                {"Stage Name": "gold", "Platform": "Power BI", "Source or Business Side": "business"}
            ])
            
            mock_read.side_effect = lambda path, sheet: {
                'Artifacts': artifacts_df,
                'Stages': stages_df,
                'Columns': pd.DataFrame()
            }[sheet]
            
            target_artifact = artifacts_df.iloc[0]
            relation_type = UpstreamRelationType.PBI
            
            result = cascading_engine._cascade_by_relation_type(
                target_artifact, artifacts_df, pd.DataFrame(), stages_df, relation_type
            )
            
            # PBI relation should return empty list
            assert result == []
    
    def test_technical_columns_creation(self, cascading_engine):
        """Test creation of technical columns for different stages."""
        # Test bronze technical columns
        bronze_columns = cascading_engine._create_technical_columns(
            'bronze', 
            pd.Series({'Artifact ID': 1, 'Artifact Name': 'test'}), 
            'SQL Server'
        )
        
        assert len(bronze_columns) > 0
        column_names = [col['Column Name'] for col in bronze_columns]
        assert '__SourceSystem' in column_names
        assert '__bronze_insertDT' in column_names
        
        # Test silver technical columns
        silver_columns = cascading_engine._create_technical_columns(
            'silver',
            pd.Series({'Artifact ID': 2, 'Artifact Name': 'test'}),
            'Databricks'
        )
        
        assert len(silver_columns) > 0
        column_names = [col['Column Name'] for col in silver_columns]
        assert '__silver_lastChanged_DT' in column_names
    
    def test_dimension_artifact_detection(self, cascading_engine):
        """Test detection of dimension artifacts."""
        # Test dimension artifact
        dim_artifact = pd.Series({'Artifact Name': 'dim_customer'})
        assert cascading_engine._is_dimension_artifact(dim_artifact) is True
        
        # Test non-dimension artifact
        fact_artifact = pd.Series({'Artifact Name': 'fact_sales'})
        assert cascading_engine._is_dimension_artifact(fact_artifact) is False
    
    def test_config_file_creation(self, cascading_engine):
        """Test creation of cascading configuration file."""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as temp_file:
            temp_config_path = temp_file.name
        
        try:
            cascading_engine.config_path = temp_config_path
            result = cascading_engine.create_cascading_config_file()
            
            assert result is True
            assert os.path.exists(temp_config_path)
            
            # Verify file contents
            data_types_df = pd.read_excel(temp_config_path, sheet_name='DataTypeMappings')
            technical_cols_df = pd.read_excel(temp_config_path, sheet_name='TechnicalColumns')
            
            assert not data_types_df.empty
            assert not technical_cols_df.empty
            
        finally:
            if os.path.exists(temp_config_path):
                os.unlink(temp_config_path)


class TestCascadingConfigManager:
    """Test the cascading configuration manager."""
    
    @pytest.fixture
    def config_manager(self):
        """Create a config manager instance."""
        return CascadingConfigManager()
    
    def test_data_type_mappings_creation(self, config_manager):
        """Test creation of data type mappings."""
        mappings = config_manager._create_data_type_mappings()
        
        assert not mappings.empty
        assert len(mappings.columns) == 3
        assert 'SQL Server Data Type' in mappings.columns
        assert 'Databricks SQL Data Type' in mappings.columns
        assert 'Power BI Data Type' in mappings.columns
        
        # Check for common data types
        sql_types = mappings['SQL Server Data Type'].tolist()
        assert 'INT' in sql_types
        assert 'VARCHAR' in sql_types
        assert 'DATETIME' in sql_types
    
    def test_technical_columns_creation(self, config_manager):
        """Test creation of technical columns configuration."""
        tech_cols = config_manager._create_technical_columns()
        
        assert not tech_cols.empty
        assert 'Stage' in tech_cols.columns
        assert 'Column Name' in tech_cols.columns
        assert 'Data Type' in tech_cols.columns
        assert 'Optional' in tech_cols.columns
        
        # Check for required stages
        stages = tech_cols['Stage'].unique()
        assert 'bronze' in stages
        assert 'silver' in stages
        assert 'gold' in stages
    
    def test_config_file_creation(self, config_manager):
        """Test creation of complete configuration file."""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            result = config_manager.create_default_config_file(temp_path)
            
            assert result is True
            assert os.path.exists(temp_path)
            
            # Verify file has both sheets
            xl = pd.ExcelFile(temp_path)
            assert 'DataTypeMappings' in xl.sheet_names
            assert 'TechnicalColumns' in xl.sheet_names
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestWorkbenchManagerIntegration:
    """Test integration of cascading with workbench manager."""
    
    @pytest.fixture
    def temp_project_dir(self):
        """Create a temporary project directory structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_path = Path(temp_dir) / "test_project"
            workbench_dir = project_path / "2_workbench"
            workbench_dir.mkdir(parents=True, exist_ok=True)
            
            # Create a test workbook
            workbook_path = workbench_dir / "workbench_test.xlsx"
            
            # Create test data
            stages_data = pd.DataFrame([
                {"Stage Name": "bronze", "Platform": "SQL Server"},
                {"Stage Name": "silver", "Platform": "Databricks"}
            ])
            
            artifacts_data = pd.DataFrame([
                {"Artifact ID": 1, "Artifact Name": "raw_data", "Stage Name": "bronze", "Upstream Relation": "", "Upstream Artifact": ""},
                {"Artifact ID": 2, "Artifact Name": "clean_data", "Stage Name": "silver", "Upstream Relation": "main", "Upstream Artifact": "1"}
            ])
            
            columns_data = pd.DataFrame([
                {"Column ID": 1, "Column Name": "id", "Artifact ID": 1, "Data Type": "INT"},
                {"Column ID": 2, "Column Name": "name", "Artifact ID": 1, "Data Type": "VARCHAR"}
            ])
            
            with pd.ExcelWriter(str(workbook_path), engine='openpyxl') as writer:
                stages_data.to_excel(writer, sheet_name='Stages', index=False)
                artifacts_data.to_excel(writer, sheet_name='Artifacts', index=False)
                columns_data.to_excel(writer, sheet_name='Columns', index=False)
            
            yield str(project_path)
    
    def test_workbench_manager_cascading_integration(self, temp_project_dir):
        """Test that workbench manager properly integrates cascading."""
        # Initialize workbench manager
        workbench_manager = WorkbenchManager(temp_project_dir)
        
        # Check that cascading engine is initialized
        assert workbench_manager.cascading_engine is not None
        assert workbench_manager.workbook_path is not None
    
    def test_get_artifacts_with_upstream(self, temp_project_dir):
        """Test getting artifacts with upstream relationships."""
        workbench_manager = WorkbenchManager(temp_project_dir)
        
        artifacts = workbench_manager.get_artifacts_with_upstream()
        
        assert len(artifacts) == 1  # Only one artifact has upstream relationship
        assert artifacts[0]['Artifact Name'] == 'clean_data'
        assert artifacts[0]['Upstream Relation'] == 'main'
    
    def test_cascading_preview(self, temp_project_dir):
        """Test cascading preview functionality."""
        workbench_manager = WorkbenchManager(temp_project_dir)
        
        preview = workbench_manager.get_cascading_preview(2)  # clean_data artifact
        
        assert 'error' not in preview
        assert preview['artifact_id'] == 2
        assert preview['upstream_relation'] == 'main'
    
    @patch.object(ColumnCascadingEngine, 'cascade_columns_for_artifact')
    def test_cascade_specific_artifact(self, mock_cascade, temp_project_dir):
        """Test cascading for a specific artifact."""
        mock_cascade.return_value = True
        
        workbench_manager = WorkbenchManager(temp_project_dir)
        result = workbench_manager.cascade_columns_for_artifact(2)
        
        assert result is True
        mock_cascade.assert_called_once_with(2)
    
    @patch.object(ColumnCascadingEngine, 'create_cascading_config_file')
    def test_create_cascading_config(self, mock_create_config, temp_project_dir):
        """Test creating cascading configuration."""
        mock_create_config.return_value = True
        
        workbench_manager = WorkbenchManager(temp_project_dir)
        result = workbench_manager.create_cascading_config()
        
        assert result is True
        mock_create_config.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
