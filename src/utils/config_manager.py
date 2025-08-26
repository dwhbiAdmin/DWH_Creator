"""
Configuration Manager
====================

Handles application configuration, settings, and constants.
"""

class ConfigManager:
    """Manages application configuration and settings."""
    
    # Default project structure
    DEFAULT_FOLDERS = [
        "1_sources",
        "2_workbench", 
        "3_templates",
        "4_artifacts",
        "9_archive"
    ]
    
    # Default stage configuration
    DEFAULT_STAGES = [
        {"id": "s1", "name": "0_drop_zone", "color": "gray"},
        {"id": "s2", "name": "1_bronze", "color": "bronze"},
        {"id": "s3", "name": "2_silver", "color": "silver"},
        {"id": "s4", "name": "3_gold", "color": "gold"},
        {"id": "s5", "name": "4_mart", "color": "blue"},
        {"id": "s6", "name": "5_PBI_Model", "color": "purple"},
        {"id": "s7", "name": "6_PBI_Reports", "color": "green"}
    ]
    
    def __init__(self):
        """Initialize configuration manager."""
        pass
    
    def get_default_project_structure(self) -> dict:
        """Get default project folder structure."""
        # TODO: Return complete project structure
        pass
    
    def get_excel_headers(self, sheet_name: str) -> list:
        """Get default headers for Excel sheets."""
        # TODO: Return appropriate headers for each sheet
        pass
