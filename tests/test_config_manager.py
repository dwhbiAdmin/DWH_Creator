"""
Unit Tests for ConfigManager
============================

Tests for the ConfigManager class that handles workbook schema configurations.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.B_worksheet_config_manager import ConfigManager


class TestConfigManager:
    """Test cases for ConfigManager."""
    
    @pytest.fixture
    def config_manager(self):
        """Create a ConfigManager instance for testing."""
        return ConfigManager()
    
    def test_initialization(self, config_manager):
        """Test ConfigManager initializes correctly."""
        assert config_manager is not None
        assert hasattr(config_manager, 'get_stages_sheet_config')
        assert hasattr(config_manager, 'get_artifacts_sheet_config')
        assert hasattr(config_manager, 'get_columns_sheet_config')
    
    @pytest.mark.unit
    def test_get_stages_sheet_config(self, config_manager):
        """Test stages sheet configuration."""
        config = config_manager.get_stages_sheet_config()
        
        # Verify return type
        assert isinstance(config, dict)
        
        # Verify required keys
        assert 'headers' in config
        assert 'default_data' in config
        
        # Verify headers structure
        headers = config['headers']
        expected_headers = [
            'Stage ID',
            'Stage Name', 
            'Stage Color',
            'Platform',
            'Source or Business Side',
            'Stage DDL Default Templates',
            'Stage ETL Default Templates'
        ]
        
        assert headers == expected_headers
    
    @pytest.mark.unit
    def test_get_artifacts_sheet_config(self, config_manager):
        """Test artifacts sheet configuration."""
        config = config_manager.get_artifacts_sheet_config()
        
        # Verify return type
        assert isinstance(config, dict)
        
        # Verify required keys
        assert 'headers' in config
        assert 'default_data' in config
        
        # Verify headers structure
        headers = config['headers']
        assert isinstance(headers, list)
        assert len(headers) > 0
    
    @pytest.mark.unit
    def test_get_columns_sheet_config(self, config_manager):
        """Test columns sheet configuration."""
        config = config_manager.get_columns_sheet_config()
        
        # Verify return type
        assert isinstance(config, dict)
        
        # Verify required keys
        assert 'headers' in config
        assert 'default_data' in config
        
        # Verify headers structure
        headers = config['headers']
        assert isinstance(headers, list)
        assert len(headers) > 0
    
    @pytest.mark.unit
    def test_stages_default_data(self, config_manager):
        """Test stages default data is correct."""
        config = config_manager.get_stages_sheet_config()
        default_data = config['default_data']
        
        assert isinstance(default_data, list)
        assert len(default_data) > 0
        
        # Check first row structure
        first_row = default_data[0]
        assert isinstance(first_row, dict)
        
        # Verify required keys exist
        required_keys = ['stage_id', 'stage_name', 'platform']
        for key in required_keys:
            assert key in first_row
        
        # Verify data types
        for row in default_data:
            assert isinstance(row, dict)
            assert isinstance(row.get('stage_name', ''), str)
            assert isinstance(row.get('platform', ''), str)
    
    @pytest.mark.unit
    def test_artifacts_default_data(self, config_manager):
        """Test artifacts default data is correct."""
        config = config_manager.get_artifacts_sheet_config()
        default_data = config['default_data']
        
        assert isinstance(default_data, list)
        # Default data might be empty for artifacts - that's okay
    
    @pytest.mark.unit
    def test_columns_default_data(self, config_manager):
        """Test columns default data is correct."""
        config = config_manager.get_columns_sheet_config()
        default_data = config['default_data']
        
        assert isinstance(default_data, list)
        # Default data might be empty for columns - that's okay
    
    @pytest.mark.unit
    def test_config_consistency(self, config_manager):
        """Test that configurations are consistent."""
        stages_config = config_manager.get_stages_sheet_config()
        artifacts_config = config_manager.get_artifacts_sheet_config()
        columns_config = config_manager.get_columns_sheet_config()
        
        # All configs should have same structure
        for config in [stages_config, artifacts_config, columns_config]:
            assert 'headers' in config
            assert 'default_data' in config
            assert isinstance(config['headers'], list)
            assert isinstance(config['default_data'], list)
    
    @pytest.mark.unit
    def test_headers_are_strings(self, config_manager):
        """Test that all headers are strings."""
        configs = [
            config_manager.get_stages_sheet_config(),
            config_manager.get_artifacts_sheet_config(),
            config_manager.get_columns_sheet_config()
        ]
        
        for config in configs:
            headers = config['headers']
            for header in headers:
                assert isinstance(header, str), f"Header '{header}' should be string"
                assert len(header) > 0, f"Header '{header}' should not be empty"
    
    @pytest.mark.unit
    def test_default_data_structure(self, config_manager):
        """Test that default data has proper structure."""
        configs = [
            ('stages', config_manager.get_stages_sheet_config()),
            ('artifacts', config_manager.get_artifacts_sheet_config()),
            ('columns', config_manager.get_columns_sheet_config())
        ]
        
        for config_name, config in configs:
            default_data = config['default_data']
            if default_data:  # Only test if there is default data
                for item in default_data:
                    assert isinstance(item, dict), f"Default data items in {config_name} should be dictionaries"
    
    @pytest.mark.unit 
    def test_stage_name_references(self, config_manager):
        """Test that stage names in default data are consistent."""
        stages_config = config_manager.get_stages_sheet_config()
        
        # Get stage names from stages default data
        stage_names = set()
        if stages_config['default_data']:
            for row in stages_config['default_data']:
                if 'stage_name' in row:
                    stage_names.add(row['stage_name'])
        
        # Basic validation that we got some stage names
        assert len(stage_names) > 0, "Should have at least one stage name"
    
    @pytest.mark.unit
    def test_stage_ids_exist(self, config_manager):
        """Test that stage IDs exist in default data."""
        config = config_manager.get_stages_sheet_config()
        default_data = config['default_data']
        
        if default_data:
            for row in default_data:
                # Should have stage_id key
                assert 'stage_id' in row, f"Stage data should have stage_id: {row}"
                # Stage ID should not be empty
                assert row['stage_id'], f"Stage ID should not be empty: {row}"
