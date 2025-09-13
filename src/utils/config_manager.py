"""
Configuration Manager
====================

Handles application configuration, settings, and constants.
"""

# ANCHOR: ConfigManager Class Definition

class ConfigManager:
    """Manages application configuration and settings."""
    
    # ANCHOR: Default Configuration Constants
    # Default project structure
    DEFAULT_SUBDIRECTORIES = [
        "1_sources",
        "2_workbench", 
        "4_artifacts",
        "9_archive"
    ]
    
    # Default stage configuration
    DEFAULT_STAGES = [
        {
            "stage_id": "s0", 
            "stage_name": "0_drop_zone", 
            "stage_color": "gray",
            "stage_technical_columns": "source_name;partition_field;created_timestamp;batch_id",
            "stage_ddl_default_templates": "drop_zone_table_ddl.sql",
            "stage_etl_default_templates": "source_to_drop_zone_etl.sql"
        },
        {
            "stage_id": "s1", 
            "stage_name": "1_bronze", 
            "stage_color": "bronze",
            "stage_technical_columns": "source_name;partition_field;created_timestamp;batch_id;record_hash",
            "stage_ddl_default_templates": "bronze_table_ddl.sql",
            "stage_etl_default_templates": "drop_zone_to_bronze_etl.sql"
        },
        {
            "stage_id": "s2", 
            "stage_name": "2_silver", 
            "stage_color": "silver",
            "stage_technical_columns": "created_timestamp;updated_timestamp;batch_id;is_active;effective_date;end_date",
            "stage_ddl_default_templates": "silver_table_ddl.sql",
            "stage_etl_default_templates": "bronze_to_silver_etl.sql"
        },
        {
            "stage_id": "s3", 
            "stage_name": "3_gold", 
            "stage_color": "gold",
            "stage_technical_columns": "created_timestamp;updated_timestamp;batch_id",
            "stage_ddl_default_templates": "gold_table_ddl.sql",
            "stage_etl_default_templates": "silver_to_gold_etl.sql"
        },
        {
            "stage_id": "s4", 
            "stage_name": "4_mart", 
            "stage_color": "blue",
            "stage_technical_columns": "created_timestamp;updated_timestamp",
            "stage_ddl_default_templates": "mart_table_ddl.sql;mart_view_ddl.sql",
            "stage_etl_default_templates": "gold_to_mart_etl.sql"
        },
        {
            "stage_id": "s5", 
            "stage_name": "5_PBI_Model", 
            "stage_color": "purple",
            "stage_technical_columns": "",
            "stage_ddl_default_templates": "",
            "stage_etl_default_templates": ""
        },
        {
            "stage_id": "s6", 
            "stage_name": "6_PBI_Reports", 
            "stage_color": "green",
            "stage_technical_columns": "",
            "stage_ddl_default_templates": "",
            "stage_etl_default_templates": ""
        }
    ]
    
    def __init__(self):
        """Initialize configuration manager."""
        pass
    
    def get_default_subdirectories(self) -> list:
        """
        Get default project folder structure.
        
        Returns:
            list: List of default subdirectory names
        """
        return self.DEFAULT_SUBDIRECTORIES.copy()
    
    def get_stages_sheet_config(self) -> dict:
        """
        Get configuration for Stages sheet.
        
        Returns:
            dict: Sheet configuration with headers and default data
        """
        headers = [
            "Stage ID",
            "Stage Name", 
            "Stage Color",
            "Stage Technical Columns",
            "Stage DDL Default Templates",
            "Stage ETL Default Templates"
        ]
        
        return {
            'headers': headers,
            'default_data': self.DEFAULT_STAGES
        }
    
    def get_artifacts_sheet_config(self) -> dict:
        """
        Get configuration for Artifacts sheet.
        
        Returns:
            dict: Sheet configuration with headers
        """
        headers = [
            "Stage ID",
            "Stage Name",
            "Artifact ID", 
            "Artifact Name",
            "Upstream Artifacts",
            "Downstream Artifacts",
            "Artifact Comment",
            "Readable Column Name",
            "Artifact Topology",
            "Upstream Relations",
            "Upstream Relation Types",
            "Artifact Relation Direction",
            "Artifact Domain",
            "DDL Template",
            "ETL Template",
            "DDL Production File",
            "ETL Production File"
        ]
        
        return {
            'headers': headers,
            'default_data': []  # Empty by default, user will populate
        }
    
    def get_columns_sheet_config(self) -> dict:
        """
        Get configuration for Columns sheet.
        
        Returns:
            dict: Sheet configuration with headers
        """
        headers = [
            "Artifact ID",
            "Column ID",
            "Column Name",
            "Order",
            "Data Type",
            "Column Comment",
            "Column Group",
            "Simple Calculation"
        ]
        
        return {
            'headers': headers,
            'default_data': []  # Empty by default, user will populate
        }
    
    def get_excel_headers(self, sheet_name: str) -> list:
        """
        Get default headers for Excel sheets.
        
        Args:
            sheet_name: Name of the sheet
            
        Returns:
            list: List of header names
        """
        if sheet_name.lower() == 'stages':
            return self.get_stages_sheet_config()['headers']
        elif sheet_name.lower() == 'artifacts':
            return self.get_artifacts_sheet_config()['headers']
        elif sheet_name.lower() == 'columns':
            return self.get_columns_sheet_config()['headers']
        else:
            return []
    
    def get_column_groups(self) -> list:
        """
        Get default column group options.
        
        Returns:
            list: List of column group names
        """
        return [
            "PKs",           # Primary Keys
            "SKs",           # Surrogate Keys  
            "BKs",           # Business Keys
            "attributes",    # Regular attributes
            "facts",         # Fact measures
            "technical_fields"  # Technical/audit columns
        ]
    
    def get_relation_types(self) -> list:
        """
        Get available relation types.
        
        Returns:
            list: List of relation type names
        """
        return [
            "source",        # Solid line
            "lookup",        # Dotted line
            "pbi_lookup"     # Diagram only (Power BI)
        ]
    
    def get_relation_directions(self) -> list:
        """
        Get Power BI relation directions.
        
        Returns:
            list: List of relation directions
        """
        return [
            "1-m",           # One to many
            "m-m",           # Many to many
            "single_forward", # Single direction forward
            "both_directions" # Bidirectional
        ]
