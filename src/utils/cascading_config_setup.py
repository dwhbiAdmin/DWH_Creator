"""
Column Cascading Configuration Setup
==================================

Sets up default configuration files for column cascading functionality.
"""

# ANCHOR: Imports and Dependencies
import pandas as pd
from pathlib import Path
import sys

# Import utilities
current_dir = Path(__file__).parent
src_dir = current_dir.parent
sys.path.insert(0, str(src_dir))

from utils.excel_utils import ExcelUtils
from utils.logger import Logger

# ANCHOR: CascadingConfigManager Class
class CascadingConfigManager:
    """Manages cascading configuration setup and defaults."""
    
    def __init__(self):
        self.excel_utils = ExcelUtils()
        self.logger = Logger()
    
    # ANCHOR: Project Configuration Methods
    def create_project_config_file(self, config_path: str, project_name: str) -> bool:
        """
        Create project-specific cascading configuration file.
        
        Args:
            config_path: Path where to create the configuration file
            project_name: Name of the project (for project-specific settings)
            
        Returns:
            bool: True if configuration file created successfully
        """
        try:
            # Create data type mappings DataFrame
            data_type_mappings = self._create_data_type_mappings()
            
            # Create technical columns DataFrame with project-specific settings
            technical_columns = self._create_technical_columns(project_name)
            
            # Write to Excel file with multiple sheets
            with pd.ExcelWriter(config_path, engine='openpyxl') as writer:
                data_type_mappings.to_excel(writer, sheet_name='DataTypeMappings', index=False)
                technical_columns.to_excel(writer, sheet_name='TechnicalColumns', index=False)
            
            self.logger.info(f"Created project-specific cascading configuration file: {config_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create configuration file: {str(e)}")
            return False
    
    def create_default_config_file(self, config_path: str) -> bool:
        """Create default cascading configuration file (backward compatibility)."""
        return self.create_project_config_file(config_path, "DefaultProject")
    
    def _create_data_type_mappings(self) -> pd.DataFrame:
        """Create comprehensive data type mappings."""
        mappings = [
            # Integer Types
            ("INT", "INT", "Whole Number"),
            ("BIGINT", "BIGINT", "Whole Number"),
            ("SMALLINT", "SMALLINT", "Whole Number"),
            ("TINYINT", "TINYINT", "Whole Number"),
            
            # Boolean Type
            ("BIT", "BOOLEAN", "True/False"),
            
            # Decimal Types
            ("DECIMAL", "DECIMAL", "Decimal Number"),
            ("NUMERIC", "DECIMAL", "Decimal Number"),
            ("MONEY", "DECIMAL", "Currency"),
            ("SMALLMONEY", "DECIMAL", "Currency"),
            
            # Float Types
            ("FLOAT", "DOUBLE", "Decimal Number"),
            ("REAL", "FLOAT", "Decimal Number"),
            
            # String Types
            ("CHAR", "STRING", "Text"),
            ("VARCHAR", "STRING", "Text"),
            ("TEXT", "STRING", "Text"),
            ("NCHAR", "STRING", "Text"),
            ("NVARCHAR", "STRING", "Text"),
            ("NTEXT", "STRING", "Text"),
            
            # Date/Time Types
            ("DATE", "DATE", "Date"),
            ("DATETIME", "TIMESTAMP", "Date/Time"),
            ("DATETIME2", "TIMESTAMP", "Date/Time"),
            ("SMALLDATETIME", "TIMESTAMP", "Date/Time"),
            ("DATETIMEOFFSET", "TIMESTAMP", "Date/Time"),
            ("TIME", "STRING", "Time"),
            
            # Binary Types
            ("BINARY", "BINARY", "Binary"),
            ("VARBINARY", "BINARY", "Binary"),
            ("IMAGE", "BINARY", "Binary"),
            
            # Special Types
            ("UNIQUEIDENTIFIER", "STRING", "Text"),
            ("XML", "STRING", "Text"),
            ("JSON", "STRING", "Text"),
            ("GEOGRAPHY", "STRING", "Text"),
            ("GEOMETRY", "STRING", "Text"),
            ("HIERARCHYID", "STRING", "Text"),
            ("SQL_VARIANT", "STRING", "Text"),
            
            # Additional Databricks Types
            ("STRING", "STRING", "Text"),
            ("TIMESTAMP", "TIMESTAMP", "Date/Time"),
            ("BOOLEAN", "BOOLEAN", "True/False"),
            ("DOUBLE", "DOUBLE", "Decimal Number"),
            ("ARRAY", "ARRAY", "Text"),
            ("MAP", "MAP", "Text"),
            ("STRUCT", "STRUCT", "Text")
        ]
        
        return pd.DataFrame(mappings, columns=[
            "sql_server",
            "databricks", 
            "power_bi"
        ])
    
    def _create_technical_columns(self, project_name: str = "DefaultProject") -> pd.DataFrame:
        """Create technical columns configuration with project-specific naming."""
        technical_columns = [
            # Bronze Stage Technical Columns
            {"Stage": "bronze", "Column Name": "__SourceSystem", "Data Type": "STRING", "Optional": False, "Description": "Source system identifier"},
            {"Stage": "bronze", "Column Name": "__SourceFileName", "Data Type": "STRING", "Optional": False, "Description": "Original source file name"},
            {"Stage": "bronze", "Column Name": "__SourceFilePath", "Data Type": "STRING", "Optional": False, "Description": "Source file path"},
            {"Stage": "bronze", "Column Name": "__bronze_insertDT", "Data Type": "TIMESTAMP", "Optional": False, "Description": "Bronze insertion timestamp"},
            {"Stage": "bronze", "Column Name": "__bronzePartition_InsertYear", "Data Type": "INT", "Optional": False, "Description": "Partition year for bronze data"},
            {"Stage": "bronze", "Column Name": "__bronzePartition_InsertMonth", "Data Type": "INT", "Optional": False, "Description": "Partition month for bronze data"},
            {"Stage": "bronze", "Column Name": "__bronzePartition_insertDate", "Data Type": "INT", "Optional": False, "Description": "Partition date for bronze data"},
            {"Stage": "bronze", "Column Name": "__bronze_hash", "Data Type": "STRING", "Optional": True, "Description": "Data hash for change detection"},
            {"Stage": "bronze", "Column Name": "__bronze_status", "Data Type": "STRING", "Optional": True, "Description": "Processing status"},
            
            # Silver Stage Technical Columns
            {"Stage": "silver", "Column Name": "__silver_lastChanged_DT", "Data Type": "TIMESTAMP", "Optional": False, "Description": "Silver last changed timestamp"},
            {"Stage": "silver", "Column Name": "__silverPartition_xxxYear", "Data Type": "INT", "Optional": True, "Description": "Silver partition year (xxx = business date field)"},
            {"Stage": "silver", "Column Name": "__silverPartition_xxxMonth", "Data Type": "INT", "Optional": True, "Description": "Silver partition month (xxx = business date field)"},
            {"Stage": "silver", "Column Name": "__silverPartition_xxxDate", "Data Type": "INT", "Optional": True, "Description": "Silver partition date (xxx = business date field)"},
            {"Stage": "silver", "Column Name": "__silver_validFrom", "Data Type": "TIMESTAMP", "Optional": True, "Description": "Valid from timestamp for SCD Type 2"},
            {"Stage": "silver", "Column Name": "__silver_validTo", "Data Type": "TIMESTAMP", "Optional": True, "Description": "Valid to timestamp for SCD Type 2"},
            {"Stage": "silver", "Column Name": "__silver_isCurrent", "Data Type": "BOOLEAN", "Optional": True, "Description": "Current record flag for SCD Type 2"},
            {"Stage": "silver", "Column Name": "__silver_hash", "Data Type": "STRING", "Optional": True, "Description": "Data hash for change detection"},
            
            # Gold Stage Technical Columns
            {"Stage": "gold", "Column Name": "__gold_lastChanged_DT", "Data Type": "TIMESTAMP", "Optional": False, "Description": "Gold last changed timestamp"},
            {"Stage": "gold", "Column Name": "__goldPartition_XXXYear", "Data Type": "INT", "Optional": True, "Description": "Gold partition year (XXX = business date field)"},
            {"Stage": "gold", "Column Name": "__goldPartition_XXXMonth", "Data Type": "INT", "Optional": True, "Description": "Gold partition month (XXX = business date field)"},
            {"Stage": "gold", "Column Name": "__goldPartition_XXXDate", "Data Type": "INT", "Optional": True, "Description": "Gold partition date (XXX = business date field)"},
            {"Stage": "gold", "Column Name": "__gold_aggregation_level", "Data Type": "STRING", "Optional": True, "Description": "Aggregation level for fact tables"},
            {"Stage": "gold", "Column Name": "__gold_measure_type", "Data Type": "STRING", "Optional": True, "Description": "Measure type classification"},
            {"Stage": "gold", "Column Name": "__gold_quality_score", "Data Type": "DECIMAL", "Optional": True, "Description": "Data quality score"},
            
            # Common Audit Columns (all stages)
            {"Stage": "bronze", "Column Name": "__audit_created_by", "Data Type": "STRING", "Optional": True, "Description": "Created by user/process"},
            {"Stage": "bronze", "Column Name": "__audit_created_date", "Data Type": "TIMESTAMP", "Optional": True, "Description": "Created date"},
            {"Stage": "bronze", "Column Name": "__audit_modified_by", "Data Type": "STRING", "Optional": True, "Description": "Modified by user/process"},
            {"Stage": "bronze", "Column Name": "__audit_modified_date", "Data Type": "TIMESTAMP", "Optional": True, "Description": "Modified date"},
            
            {"Stage": "silver", "Column Name": "__audit_created_by", "Data Type": "STRING", "Optional": True, "Description": "Created by user/process"},
            {"Stage": "silver", "Column Name": "__audit_created_date", "Data Type": "TIMESTAMP", "Optional": True, "Description": "Created date"},
            {"Stage": "silver", "Column Name": "__audit_modified_by", "Data Type": "STRING", "Optional": True, "Description": "Modified by user/process"},
            {"Stage": "silver", "Column Name": "__audit_modified_date", "Data Type": "TIMESTAMP", "Optional": True, "Description": "Modified date"},
            
            {"Stage": "gold", "Column Name": "__audit_created_by", "Data Type": "STRING", "Optional": True, "Description": "Created by user/process"},
            {"Stage": "gold", "Column Name": "__audit_created_date", "Data Type": "TIMESTAMP", "Optional": True, "Description": "Created date"},
            {"Stage": "gold", "Column Name": "__audit_modified_by", "Data Type": "STRING", "Optional": True, "Description": "Modified by user/process"},
            {"Stage": "gold", "Column Name": "__audit_modified_date", "Data Type": "TIMESTAMP", "Optional": True, "Description": "Modified date"}
        ]
        
        return pd.DataFrame(technical_columns)

def main():
    """Create default configuration file."""
    config_manager = CascadingConfigManager()
    
    # Create in current directory for testing
    config_path = Path(__file__).parent / "cascading_config_default.xlsx"
    
    success = config_manager.create_default_config_file(str(config_path))
    
    if success:
        print(f"Successfully created configuration file: {config_path}")
    else:
        print("Failed to create configuration file")

if __name__ == "__main__":
    main()
