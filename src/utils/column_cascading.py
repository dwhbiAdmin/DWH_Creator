"""
Column Cascading Engine
======================

Handles automatic column propagation between stages based on upstream relationships.
Supports main, get_key, lookup, and pbi cascading patterns with platform-specific
data type mapping and technical column injection.
"""

# ANCHOR: Imports and Dependencies
import pandas as pd
from pathlib import Path
import sys
from typing import Dict, List, Optional, Tuple
from enum import Enum

# Import utilities with proper path handling
current_dir = Path(__file__).parent
src_dir = current_dir.parent
sys.path.insert(0, str(src_dir))

from utils.excel_utils import ExcelUtils
from utils.logger import Logger
from utils.config_manager import ConfigManager
from utils.relation_processor import RelationProcessor, ArtifactType

# ANCHOR: Enums and Constants
class UpstreamRelationType(Enum):
    """Types of upstream relationships for cascading."""
    MAIN = "main"
    GET_KEY = "get_key"
    LOOKUP = "lookup"
    PBI = "pbi"

class PlatformType(Enum):
    """Supported platform types."""
    SQL_SERVER = "SQL Server"
    DATABRICKS = "Databricks"
    POWER_BI = "Power BI"

# ANCHOR: Column Cascading Engine Class
class ColumnCascadingEngine:
    """
    Handles automatic column cascading between data warehouse stages.
    """
    
    def __init__(self, workbook_path: str, config_path: str = None):
        """
        Initialize the Column Cascading Engine.
        
        Args:
            workbook_path: Path to the main workbook
            config_path: Optional path to cascading config file
        """
        self.workbook_path = workbook_path
        self.config_path = config_path or self._get_default_config_path()
        self.excel_utils = ExcelUtils()
        self.logger = Logger()
        self.config_manager = ConfigManager()
        
        # Initialize enhanced relation processor
        self.relation_processor = RelationProcessor()
        
        # Initialize global column ID tracking
        self._global_column_id_counter = None
        
        # Load configuration data
        self._load_cascading_configs()
    
    def _get_default_config_path(self) -> str:
        """Get default cascading configuration file path."""
        workbook_dir = Path(self.workbook_path).parent
        workbook_name = Path(self.workbook_path).stem
        
        # Extract project name from workbook name (e.g., "workbench_ProjectName.xlsx")
        if workbook_name.startswith("workbench_"):
            project_name = workbook_name[10:]  # Remove "workbench_" prefix
            project_specific_config = workbook_dir / f"cascading_config_{project_name}.xlsx"
            
            # Check if project-specific config exists
            if project_specific_config.exists():
                return str(project_specific_config)
        
        # Fallback to generic config
        return str(workbook_dir / "cascading_config.xlsx")
    
    def _load_cascading_configs(self):
        """Load cascading configuration data."""
        try:
            # Load data type mappings
            self.data_type_mappings = self._load_data_type_mappings()
            
            # Load technical columns configuration
            self.technical_columns_config = self._load_technical_columns_config()
            
            self.logger.info("Cascading configurations loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load cascading configurations: {str(e)}")
            # Initialize with empty configs if loading fails
            self.data_type_mappings = pd.DataFrame()
            self.technical_columns_config = {}
    
    def regenerate_all_columns_with_unique_ids(self, include_technical_fields: bool = True) -> bool:
        """
        Regenerate ALL columns with globally unique IDs and proper ordering.
        This clears existing columns and regenerates from scratch.
        
        Args:
            include_technical_fields: Whether to include technical fields in cascading
            
        Returns:
            bool: True if regeneration was successful
        """
        self.logger.info("Starting complete column regeneration with unique IDs")
        
        try:
            # Read current workbook data
            artifacts_df = self.excel_utils.read_sheet_data(self.workbook_path, 'Artifacts')
            
            # Reset the global counter to start fresh
            self._global_column_id_counter = 0
            
            # Clear existing columns
            empty_columns_df = pd.DataFrame(columns=[
                'stage_id', 'stage_name', 'artifact_id', 'artifact_name', 'column_id', 'column_name',
                'order', 'data_type', 'column_comment', 'column_business_name', 'column_group'
            ])
            
            # Save empty columns sheet
            self.excel_utils.write_sheet_data(
                self.workbook_path, 'Columns', empty_columns_df
            )
            
            self.logger.info("Cleared existing columns, starting regeneration")
            
            # Get all artifacts that need columns
            all_artifact_ids = artifacts_df['artifact_id'].tolist()
            
            # Identify source artifacts (those without upstream relationships)
            source_artifacts = []
            downstream_artifacts = []
            
            for _, artifact in artifacts_df.iterrows():
                upstream_rel = artifact.get('upstream_relation', '')
                upstream_artifact = artifact.get('upstream_artifact', '')
                
                if pd.isna(upstream_rel) or upstream_rel == '' or pd.isna(upstream_artifact) or upstream_artifact == '':
                    source_artifacts.append(artifact['artifact_id'])
                else:
                    downstream_artifacts.append(artifact['artifact_id'])
            
            processed_artifacts = set()
            regeneration_count = 0
            
            # Process source artifacts first
            self.logger.info(f"Processing {len(source_artifacts)} source artifacts first")
            for artifact_id in source_artifacts:
                self.logger.info(f"Regenerating columns for source artifact {artifact_id}")
                success = self.cascade_columns_for_artifact(artifact_id, include_technical_fields)
                if success:
                    regeneration_count += 1
                    processed_artifacts.add(artifact_id)
                    
            # Process downstream artifacts in dependency order
            max_iterations = len(downstream_artifacts) * 2  # Prevent infinite loops
            iteration = 0
            
            while len(processed_artifacts) < len(all_artifact_ids) and iteration < max_iterations:
                iteration += 1
                made_progress = False
                
                for artifact_id in downstream_artifacts:
                    if artifact_id in processed_artifacts:
                        continue
                        
                    # Find the upstream artifact for this one
                    artifact_row = artifacts_df[artifacts_df['artifact_id'] == artifact_id]
                    if artifact_row.empty:
                        continue
                        
                    upstream_artifact = artifact_row.iloc[0].get('upstream_artifact', '')
                    
                    # Check if upstream is processed (or doesn't exist)
                    if pd.isna(upstream_artifact) or upstream_artifact == '' or upstream_artifact in processed_artifacts:
                        self.logger.info(f"Regenerating columns for artifact {artifact_id}")
                        success = self.cascade_columns_for_artifact(artifact_id, include_technical_fields)
                        if success:
                            regeneration_count += 1
                            processed_artifacts.add(artifact_id)
                            made_progress = True
                
                if not made_progress:
                    # Process any remaining artifacts that might have circular dependencies
                    for artifact_id in downstream_artifacts:
                        if artifact_id not in processed_artifacts:
                            self.logger.info(f"Regenerating columns for remaining artifact {artifact_id}")
                            success = self.cascade_columns_for_artifact(artifact_id, include_technical_fields)
                            if success:
                                regeneration_count += 1
                                processed_artifacts.add(artifact_id)
                    break
            
            self.logger.info(f"Column regeneration completed: {regeneration_count}/{len(all_artifact_ids)} artifacts processed")
            return regeneration_count > 0  # Success if we processed at least some artifacts
            
        except Exception as e:
            self.logger.error(f"Error during column regeneration: {str(e)}")
            return False

    def cascade_all_missing_artifacts(self, include_technical_fields: bool = True) -> bool:
        """
        Cascade columns for all artifacts that exist in artifacts sheet but not in columns sheet.
        This follows the correct logic: 
        1. Find artifacts missing from columns sheet
        2. For each missing artifact, get its upstream relationship
        3. Cascade columns based on the relationship type
        
        Args:
            include_technical_fields: Whether to include technical/audit columns
        
        Returns:
            bool: True if all cascading operations succeeded
        """
        try:
            self.logger.info("Starting cascade for all missing artifacts")
            
            # Load workbook data
            artifacts_df = self.excel_utils.read_sheet_data(self.workbook_path, "Artifacts")
            columns_df = self.excel_utils.read_sheet_data(self.workbook_path, "Columns")
            
            # Find artifacts that have no columns
            artifacts_with_columns = set(columns_df['artifact_id'].unique())
            all_artifacts = set(artifacts_df['artifact_id'].unique())
            missing_artifacts = all_artifacts - artifacts_with_columns
            
            if not missing_artifacts:
                self.logger.info("No missing artifacts found - all artifacts already have columns")
                return True
            
            self.logger.info(f"Found {len(missing_artifacts)} artifacts missing columns: {sorted(missing_artifacts)}")
            
            # Cascade each missing artifact
            success_count = 0
            for artifact_id in sorted(missing_artifacts):
                if self.cascade_columns_for_artifact(artifact_id, include_technical_fields=include_technical_fields):
                    success_count += 1
                else:
                    self.logger.warning(f"Failed to cascade columns for artifact {artifact_id}")
            
            self.logger.info(f"Cascading completed: {success_count}/{len(missing_artifacts)} artifacts processed successfully")
            return success_count == len(missing_artifacts)
            
        except Exception as e:
            self.logger.error(f"Error during cascade all operation: {str(e)}")
            return False
    
    def _load_data_type_mappings(self) -> pd.DataFrame:
        """Load data type mapping configuration."""
        try:
            df = self.excel_utils.read_sheet_data(self.config_path, "DataTypeMappings")
            if df.empty:
                # Create default mappings if config doesn't exist
                return self._create_default_data_type_mappings()
            return df
        except:
            return self._create_default_data_type_mappings()
    
    def _create_default_data_type_mappings(self) -> pd.DataFrame:
        """Create default data type mappings."""
        mappings = [
            ("INT", "INT", "INT64"),
            ("BIGINT", "BIGINT", "INT64"),
            ("SMALLINT", "SMALLINT", "INT64"),
            ("TINYINT", "TINYINT", "INT64"),
            ("BIT", "BOOLEAN", "Boolean"),
            ("DECIMAL", "DECIMAL", "Decimal"),
            ("NUMERIC", "NUMERIC", "Decimal"),
            ("FLOAT", "FLOAT", "Double"),
            ("REAL", "REAL", "Double"),
            ("CHAR", "CHAR", "String"),
            ("VARCHAR", "STRING", "String"),
            ("TEXT", "STRING", "String"),
            ("NCHAR", "STRING", "String"),
            ("NVARCHAR", "STRING", "String"),
            ("NTEXT", "STRING", "String"),
            ("DATE", "DATE", "Date"),
            ("DATETIME", "TIMESTAMP", "DateTime"),
            ("DATETIME2", "TIMESTAMP", "DateTime"),
            ("SMALLDATETIME", "TIMESTAMP", "DateTime"),
            ("TIME", "TIME", "Time"),
            ("BINARY", "BINARY", "Binary"),
            ("VARBINARY", "BINARY", "Binary"),
            ("IMAGE", "BINARY", "Binary"),
            ("UNIQUEIDENTIFIER", "STRING", "String")
        ]
        
        return pd.DataFrame(mappings, columns=[
            "sql_server",
            "databricks", 
            "power_bi"
        ])
    
    def _load_technical_columns_config(self) -> Dict:
        """Load technical columns configuration."""
        try:
            df = self.excel_utils.read_sheet_data(self.config_path, "TechnicalColumns")
            if df.empty:
                return self._create_default_technical_columns()
            
            # Convert DataFrame to nested dictionary structure
            config = {}
            for _, row in df.iterrows():
                stage_id = row.get('Stage_ID', '')
                stage = row.get('Stage', '')
                column_name = row.get('column_name', '')
                data_type = row.get('data_type', '')
                include_in_tech_fields = row.get('include_in_tech_fields', False)
                take_to_next_level = row.get('Take_To_Next_Level', True)
                
                # Use stage_id as primary key, fallback to stage name
                stage_key = stage_id if stage_id else stage
                
                if stage_key not in config:
                    config[stage_key] = []
                
                config[stage_key].append({
                    'column_name': column_name,
                    'data_type': data_type,
                    'include_in_tech_fields': include_in_tech_fields,
                    'take_to_next_level': take_to_next_level
                })
            
            return config
            
        except:
            return self._create_default_technical_columns()
    
    def _create_default_technical_columns(self) -> Dict:
        """Create default technical columns configuration."""
        return {
            'bronze': [
                {'column_name': '__SourceSystem', 'data_type': 'string', 'include_in_tech_fields': False},
                {'column_name': '__SourceFileName', 'data_type': 'string', 'include_in_tech_fields': False},
                {'column_name': '__SourceFilePath', 'data_type': 'string', 'include_in_tech_fields': False},
                {'column_name': '__bronze_insertDT', 'data_type': 'timestamp', 'include_in_tech_fields': False},
                {'column_name': '__bronzePartition_InsertYear', 'data_type': 'int', 'include_in_tech_fields': False},
                {'column_name': '__bronzePartition_InsertMonth', 'data_type': 'int', 'include_in_tech_fields': False},
                {'column_name': '__bronzePartition_insertDate', 'data_type': 'int', 'include_in_tech_fields': False}
            ],
            'silver': [
                {'column_name': '__silver_lastChanged_DT', 'data_type': 'timestamp', 'include_in_tech_fields': False},
                {'column_name': '__silverPartition_xxxYear', 'data_type': 'integer', 'include_in_tech_fields': True},
                {'column_name': '__silverPartition_xxxMonth', 'data_type': 'integer', 'include_in_tech_fields': True},
                {'column_name': '__silverPartition_xxxDate', 'data_type': 'integer', 'include_in_tech_fields': True}
            ],
            'gold': [
                {'column_name': '__gold_lastChanged_DT', 'data_type': 'timestamp', 'include_in_tech_fields': False},
                {'column_name': '__goldPartition_XXXYear', 'data_type': 'integer', 'include_in_tech_fields': True},
                {'column_name': '__goldPartition_XXXMonth', 'data_type': 'integer', 'include_in_tech_fields': True},
                {'column_name': '__goldPartition_XXXDate', 'data_type': 'integer', 'include_in_tech_fields': True}
            ]
        }
    
    # ANCHOR: Main Cascading Methods
    def cascade_columns_for_artifact(self, artifact_id: str, include_technical_fields: bool = True) -> bool:
        """
        Cascade columns for a specific artifact based on its upstream relationships.
        
        Args:
            artifact_id: ID of the artifact to cascade columns for
            include_technical_fields: Whether to include technical/audit columns
            
        Returns:
            bool: True if cascading was successful
        """
        try:
            self.logger.info(f"Starting column cascading for artifact {artifact_id}")
            
            # Load workbook data
            artifacts_df = self.excel_utils.read_sheet_data(self.workbook_path, "Artifacts")
            columns_df = self.excel_utils.read_sheet_data(self.workbook_path, "Columns")
            stages_df = self.excel_utils.read_sheet_data(self.workbook_path, "Stages")
            
            # Find the target artifact
            target_artifact_row = artifacts_df[artifacts_df['artifact_id'] == artifact_id]
            if target_artifact_row.empty:
                self.logger.error(f"Artifact {artifact_id} not found")
                return False
            
            target_artifact = target_artifact_row.iloc[0]
            
            # Check if artifact already has columns
            existing_columns = columns_df[columns_df['artifact_id'] == artifact_id]
            if not existing_columns.empty:
                self.logger.info(f"Artifact {artifact_id} already has columns, skipping")
                return True
            
            # Get upstream relationship information
            upstream_artifact_id = target_artifact.get('upstream_artifact', '')
            upstream_relation = target_artifact.get('upstream_relation', '')
            
            # Handle NaN values that come as float
            if pd.isna(upstream_relation):
                upstream_relation = ''
            else:
                upstream_relation = str(upstream_relation).lower().strip()
            
            if not upstream_artifact_id or not upstream_relation:
                self.logger.info(f"No upstream relationship defined for artifact {artifact_id}")
                return True
            
            # Get upstream artifact columns (handle multiple upstream artifacts)
            upstream_artifact_ids = [id.strip() for id in upstream_artifact_id.split(';')]
            upstream_relation_types = [rel.strip() for rel in upstream_relation.split(';')]
            
            # Ensure we have the same number of artifacts and relation types
            if len(upstream_artifact_ids) != len(upstream_relation_types):
                # If only one relation type provided, use it for all artifacts
                if len(upstream_relation_types) == 1:
                    upstream_relation_types = upstream_relation_types * len(upstream_artifact_ids)
                else:
                    self.logger.error(f"Mismatch between number of upstream artifacts ({len(upstream_artifact_ids)}) and relation types ({len(upstream_relation_types)})")
                    return False
            
            all_new_columns = []
            
            # Process each upstream artifact with its specific relation type
            for upstream_id, relation_type in zip(upstream_artifact_ids, upstream_relation_types):
                upstream_artifact_columns = columns_df[columns_df['artifact_id'] == upstream_id]
                if upstream_artifact_columns.empty:
                    self.logger.warning(f"No columns found for upstream artifact {upstream_id}")
                    continue
                
                # Generate columns for this specific upstream relationship
                new_columns = self._generate_columns_by_relation_type(
                    target_artifact, upstream_artifact_columns, relation_type, stages_df, include_technical_fields
                )
                
                if new_columns:
                    all_new_columns.extend(new_columns)
            
            if not all_new_columns:
                self.logger.info(f"No columns to cascade for artifact {artifact_id}")
                return True
            
            if all_new_columns:
                # Filter out duplicate column names within the artifact
                filtered_columns = self._remove_duplicate_columns(all_new_columns, columns_df, artifact_id)
                
                if filtered_columns:
                    # Add new columns to the workbook
                    updated_columns_df = pd.concat([columns_df, pd.DataFrame(filtered_columns)], ignore_index=True)
                    self.excel_utils.write_sheet_data(self.workbook_path, "Columns", updated_columns_df)
                    
                    # Apply formatting to the Columns sheet
                    self.excel_utils.apply_sheet_formatting(self.workbook_path, "Columns")
                    
                    self.logger.info(f"Successfully cascaded {len(filtered_columns)} columns for artifact {artifact_id}")
                    
                    if len(filtered_columns) < len(all_new_columns):
                        skipped = len(all_new_columns) - len(filtered_columns)
                        self.logger.info(f"Skipped {skipped} duplicate columns for artifact {artifact_id}")
                else:
                    self.logger.info(f"No new columns to add for artifact {artifact_id} (all were duplicates)")
            else:
                self.logger.info(f"No columns to cascade for artifact {artifact_id}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error cascading columns for artifact {artifact_id}: {str(e)}")
            return False
    
    def _identify_column_type(self, column_name: str) -> str:
        """
        Identify the type of column based on naming conventions.
        
        Args:
            column_name: Name of the column
            
        Returns:
            str: Column type ('business_key', 'primary_key', 'surrogate_key', 'attribute')
        """
        column_upper = column_name.upper()
        
        if column_upper.endswith('_BK'):
            return 'business_key'
        elif column_upper.endswith('_PK'):
            return 'primary_key'
        elif column_upper.endswith('_SK'):
            return 'surrogate_key'
        else:
            return 'attribute'
    
    def _is_dimension_table(self, artifact_name: str) -> bool:
        """
        Determine if an artifact is a dimension table.
        
        Args:
            artifact_name: Name of the artifact
            
        Returns:
            bool: True if this is a dimension table
        """
        artifact_lower = artifact_name.lower()
        return artifact_lower.startswith('dim_') or 'dimension' in artifact_lower
    
    def _is_fact_table(self, artifact_name: str) -> bool:
        """
        Determine if an artifact is a fact table.
        
        Args:
            artifact_name: Name of the artifact
            
        Returns:
            bool: True if this is a fact table
        """
        artifact_lower = artifact_name.lower()
        return artifact_lower.startswith('fact_') or 'fact' in artifact_lower
    
    def _generate_dimension_key_columns(self, artifact_name: str, ordinal: int, target_stage_name: str, 
                                      target_artifact_id: str) -> tuple:
        """
        Generate the standard SK and BK columns for dimension tables.
        
        Args:
            artifact_name: Name of the dimension
            ordinal: Starting ordinal number
            target_stage_name: Target stage name
            target_artifact_id: Target artifact ID
            
        Returns:
            tuple: (list of key columns, new ordinal)
        """
        key_columns = []
        
        # Generate dimension name (remove 'dim_' prefix if present)
        dim_name = artifact_name.replace('dim_', '').replace('dimension_', '')
        
        # First column: Surrogate Key
        sk_column = {
            'stage_name': target_stage_name,
            'artifact_id': target_artifact_id,
            'artifact_name': artifact_name,
            'column_id': self._get_next_column_id(),
            'column_name': f"{dim_name}_SK",
            'order': ordinal,
            'data_type': 'BIGINT',
            'column_comment': f'Surrogate key for {dim_name} dimension',
            'column_business_name': f'{dim_name}_SK',
            'column_group': 'SKs'
        }
        key_columns.append(sk_column)
        ordinal += 1
        
        # Second column: Business Key
        bk_column = {
            'stage_name': target_stage_name,
            'artifact_id': target_artifact_id,
            'artifact_name': artifact_name,
            'column_id': self._get_next_column_id(),
            'column_name': f"{dim_name}_BK",
            'order': ordinal,
            'data_type': 'BIGINT',
            'column_comment': f'Business key for {dim_name} dimension',
            'column_business_name': f'{dim_name}_BK',
            'column_group': 'BKs'
        }
        key_columns.append(bk_column)
        ordinal += 1
        
        return key_columns, ordinal

    def _should_cascade_column(self, column_name: str, relation_type: str) -> bool:
        """
        Determine if a column should be cascaded based on its type and relation type.
        
        Args:
            column_name: Name of the column
            relation_type: Type of upstream relation
            
        Returns:
            bool: Whether the column should be cascaded
        """
        column_type = self._identify_column_type(column_name)
        
        if relation_type == 'main':
            # Main relation cascades all columns
            return True
        elif relation_type == 'get_key':
            # Get_key relation only cascades key columns (BK, PK, SK)
            return column_type in ['business_key', 'primary_key', 'surrogate_key']
        elif relation_type == 'lookup':
            # Lookup relation cascades first 3 attribute columns plus all keys
            return column_type in ['business_key', 'primary_key', 'surrogate_key'] or True  # Will handle limit in main logic
        elif relation_type == 'pbi':
            # PBI relation has minimal impact
            return False
        else:
            # Default to cascading for unknown relation types
            return True

    def _should_cascade_technical_field(self, column_name: str, upstream_stage_name: str) -> bool:
        """
        Determine if a technical field from upstream stage should be cascaded forward.
        
        Args:
            column_name: Name of the technical field
            upstream_stage_name: Name of the upstream stage
            
        Returns:
            bool: Whether the technical field should be cascaded
        """
        # Get technical fields configuration for the upstream stage
        upstream_tech_fields = self._get_technical_fields_for_stage(upstream_stage_name)
        
        for tech_field in upstream_tech_fields:
            if tech_field['column_name'] == column_name:
                # Field can only cascade if:
                # 1. It was included in the upstream stage (include_in_tech_fields=True)
                # 2. It's marked to take to next level (take_to_next_level=True)
                included_in_upstream = tech_field.get('include_in_tech_fields', False)
                can_move_to_next = tech_field.get('take_to_next_level', False)
                
                return included_in_upstream and can_move_to_next
        
        # If not found in config, don't cascade
        return False

    def _generate_columns_by_relation_type(self, target_artifact: pd.Series, upstream_columns: pd.DataFrame,
                                         upstream_relation: str, stages_df: pd.DataFrame, 
                                         include_technical_fields: bool = True) -> List[Dict]:
        """
        Enhanced column generation using RelationProcessor for deterministic context-aware processing.
        
        Args:
            target_artifact: The target artifact to cascade to
            upstream_columns: DataFrame of upstream artifact columns
            upstream_relation: Type of upstream relation (main, get_key, lookup, pbi)
            stages_df: DataFrame of stage information
            include_technical_fields: Whether to include technical/audit columns
            
        Returns:
            List[Dict]: List of new column definitions
        """
        # Get target artifact information
        target_artifact_id = target_artifact['artifact_id']
        target_artifact_name = target_artifact['artifact_name']
        target_stage_name = target_artifact['stage_name']
        target_artifact_type_field = target_artifact.get('artifact_type', '')
        
        # Get source stage for context-aware processing
        source_stage_name = upstream_columns.iloc[0]['stage_name'] if not upstream_columns.empty else ''
        
        # Map stage names to stage IDs for RelationProcessor
        stage_name_to_id = {
            '0_drop_zone': 's0',
            '1_bronze': 's1',
            '2_silver': 's2', 
            '3_gold': 's3',
            '4_mart': 's4',
            '5_PBI_Model': 's5',
            '6_PBI_Reports': 's6'
        }
        
        source_stage_id = stage_name_to_id.get(source_stage_name, 's0')
        target_stage_id = stage_name_to_id.get(target_stage_name, 's1')
        
        # Detect target artifact type using RelationProcessor
        target_artifact_type = self.relation_processor.detect_artifact_type(
            target_artifact_name, target_artifact_type_field
        )
        
        self.logger.info(f"Enhanced cascading: {source_stage_id}→{target_stage_id}, "
                        f"relation: {upstream_relation}, artifact: {target_artifact_type.value}")
        
        # Convert upstream columns DataFrame to list of dictionaries for RelationProcessor
        source_columns = []
        for _, col in upstream_columns.iterrows():
            source_columns.append({
                'column_name': col['column_name'],
                'data_type': col['data_type'],
                'column_group': col.get('column_group', 'attributes'),
                'column_comment': col.get('column_comment', ''),
                'column_business_name': col.get('column_business_name', ''),
                'order': col.get('order', 0),
                'artifact_name': col.get('artifact_name', ''),
                'stage_name': col.get('stage_name', '')
            })
        
        # Use RelationProcessor for enhanced deterministic processing
        if upstream_relation == 'main':
            processed_columns = self.relation_processor.process_main_relation(
                source_columns, source_stage_id, target_stage_id, target_artifact_type
            )
        elif upstream_relation == 'get_key':
            processed_columns = self.relation_processor.process_get_key_relation(
                source_columns, target_artifact_type
            )
        elif upstream_relation == 'lookup':
            processed_columns = self.relation_processor.process_lookup_relation(
                source_columns, field_limit=3
            )
        elif upstream_relation == 'pbi':
            processed_columns = self.relation_processor.process_pbi_relation(source_columns)
        else:
            self.logger.warning(f"Unknown relation type: {upstream_relation}, falling back to main processing")
            processed_columns = self.relation_processor.process_main_relation(
                source_columns, source_stage_id, target_stage_id, target_artifact_type
            )
        
        # Convert processed columns back to the expected format for the rest of the cascading engine
        new_columns = []
        target_platform = self._get_target_platform(stages_df, target_stage_name)
        ordinal = 1
        
        for processed_col in processed_columns:
            # Convert data type for target platform
            converted_type = self._convert_data_type(processed_col['data_type'], target_platform)
            
            new_column = {
                'stage_id': target_stage_id,
                'stage_name': target_stage_name,
                'artifact_id': target_artifact_id,
                'artifact_name': target_artifact_name,
                'column_id': self._get_next_column_id(),
                'column_name': processed_col['column_name'],
                'order': processed_col.get('order', ordinal),
                'data_type': converted_type,
                'column_comment': processed_col.get('Column Comment', ''),
                'column_business_name': processed_col.get('Column Business Name', ''),
                'column_group': processed_col.get('Column Group', 'attributes')
            }
            new_columns.append(new_column)
            ordinal += 1
        
        # Apply legacy column hierarchy ordering for compatibility
        new_columns = self._reorder_columns_by_hierarchy(new_columns)
        
        # Apply primary key propagation logic for source-side artifacts
        new_columns = self._apply_primary_key_propagation(new_columns, target_artifact, stages_df)
        
        return new_columns
    
    def _apply_primary_key_propagation(self, columns: List[Dict], target_artifact: pd.Series, 
                                     stages_df: pd.DataFrame) -> List[Dict]:
        """
        Apply primary key propagation logic for source-side artifacts.
        
        Primary keys propagate downstream to all source-side artifacts.
        Business-side artifacts may have different primary key strategies.
        
        Args:
            columns: List of column dictionaries
            target_artifact: Target artifact information
            stages_df: Stage configuration DataFrame
            
        Returns:
            List[Dict]: Updated columns with primary key propagation applied
        """
        try:
            target_stage_name = target_artifact['stage_name']
            
            # Get stage configuration to determine artifact side
            stage_config = None
            if hasattr(self, 'cascading_configs') and 'StageConfiguration' in self.cascading_configs:
                stage_df = self.cascading_configs['StageConfiguration']
                stage_row = stage_df[stage_df['Stage_Name'] == target_stage_name]
                if not stage_row.empty:
                    stage_config = stage_row.iloc[0]
            
            # If no stage config found, try to determine from stage name patterns
            artifact_side = None
            if stage_config is not None:
                artifact_side = stage_config.get('Artifact_Side', 'unknown')
            else:
                # Fallback logic based on stage naming patterns
                if target_stage_name in ['0_drop_zone', '1_bronze']:
                    artifact_side = 'source'
                elif target_stage_name in ['2_silver', '3_gold', '4_mart', '5_PBI_Model', '6_PBI_Reports']:
                    artifact_side = 'business'
                else:
                    artifact_side = 'unknown'
            
            self.logger.info(f"Primary key propagation for {target_stage_name}: artifact_side={artifact_side}")
            
            # Apply primary key propagation logic
            if artifact_side == 'source':
                # For source-side artifacts, primary keys should propagate downstream
                for column in columns:
                    if column.get('Column Group', '').lower() in ['primary_key', 'primarykey', 'pk']:
                        # Ensure primary key columns maintain their group classification
                        column['Column Group'] = 'primary_key'
                        
                        # Primary keys get highest priority in ordering
                        current_order = column.get('order', 999)
                        # Ensure primary keys come first (order 0-10 range)
                        if current_order > 10:
                            column['order'] = 1
                        
                        self.logger.info(f"Primary key propagated: {column['column_name']} (order: {column['order']})")
            
            elif artifact_side == 'business':
                # For business-side artifacts, primary key handling might be different
                # Could implement surrogate key generation or other business logic here
                for column in columns:
                    if column.get('Column Group', '').lower() in ['primary_key', 'primarykey', 'pk']:
                        # Business side might transform primary keys to business keys or maintain them
                        # For now, maintain the primary key designation
                        column['Column Group'] = 'primary_key'
                        self.logger.info(f"Primary key maintained in business layer: {column['column_name']}")
            
            return columns
            
        except Exception as e:
            self.logger.warning(f"Error in primary key propagation: {str(e)}")
            return columns
    
    def _get_target_platform(self, stages_df: pd.DataFrame, target_stage_name: str) -> str:
        """Get target platform for data type conversion."""
        target_stage_row = stages_df[stages_df['stage_name'] == target_stage_name]
        return target_stage_row.iloc[0]['platform'].strip() if not target_stage_row.empty else 'Azure SQL'
    
    def _get_technical_fields_for_stage(self, stage_name: str, platform: str = 'Azure SQL') -> List[Dict]:
        """Get technical fields for a specific stage using stage_id."""
        # Map stage names to stage IDs
        stage_id_mapping = {
            '0_drop_zone': 's0',
            '1_bronze': 's1', 
            '2_silver': 's2',
            '3_gold': 's3',
            '4_mart': 's4',
            '5_PBI_Model': 's5',
            '6_PBI_Reports': 's6'
        }
        
        stage_id = stage_id_mapping.get(stage_name)
        if stage_id and stage_id in self.technical_columns_config:
            return self.technical_columns_config[stage_id]
        
        # Fallback to old logic for backward compatibility
        stage_lower = stage_name.lower()
        
        if 'bronze' in stage_lower or '1_bronze' in stage_lower:
            return self.technical_columns_config.get('s1', self.technical_columns_config.get('bronze', []))
        elif 'silver' in stage_lower or '2_silver' in stage_lower:
            return self.technical_columns_config.get('s2', self.technical_columns_config.get('silver', []))
        elif 'gold' in stage_lower or '3_gold' in stage_lower:
            return self.technical_columns_config.get('s3', self.technical_columns_config.get('gold', []))
        elif 'mart' in stage_lower or '4_mart' in stage_lower:
            return self.technical_columns_config.get('s4', [])
        elif 'pbi' in stage_lower or '5_pbi' in stage_lower:
            return self.technical_columns_config.get('s5', [])
        else:
            # Default technical field for other stages
            return [{'column_name': f'__{stage_lower}_last_changed_DT', 'data_type': 'TIMESTAMP', 'take_to_next_level': False}]
    
    def _convert_data_type(self, source_type: str, target_platform: str) -> str:
        """Convert data type based on target platform."""
        if not hasattr(self, 'data_type_mappings') or self.data_type_mappings is None or self.data_type_mappings.empty:
            return source_type
            
        source_type_clean = source_type.upper().strip()
        
        # Look for mapping in the DataFrame
        mapping_row = self.data_type_mappings[
            self.data_type_mappings['sql_server'].str.upper() == source_type_clean
        ]
        
        if mapping_row.empty:
            return source_type  # Return original if no mapping found
        
        # Map to target platform  
        if 'databricks' in target_platform.lower():
            return mapping_row.iloc[0]['databricks']
        elif 'power bi' in target_platform.lower():
            return mapping_row.iloc[0]['power_bi']
        else:  # Default to source type for same platform
            return source_type
    
    def _cascade_by_relation_type(self, target_artifact: pd.Series, artifacts_df: pd.DataFrame, 
                                columns_df: pd.DataFrame, stages_df: pd.DataFrame, 
                                relation_type: UpstreamRelationType) -> List[Dict]:
        """
        Perform cascading based on the upstream relationship type.
        
        Returns:
            List[Dict]: List of new column definitions
        """
        if relation_type == UpstreamRelationType.MAIN:
            return self._cascade_main_relation(target_artifact, artifacts_df, columns_df, stages_df)
        elif relation_type == UpstreamRelationType.GET_KEY:
            return self._cascade_get_key_relation(target_artifact, artifacts_df, columns_df, stages_df)
        elif relation_type == UpstreamRelationType.LOOKUP:
            return self._cascade_lookup_relation(target_artifact, artifacts_df, columns_df, stages_df)
        elif relation_type == UpstreamRelationType.PBI:
            return self._cascade_pbi_relation(target_artifact, artifacts_df, columns_df, stages_df)
        else:
            self.logger.warning(f"Unknown relation type: {relation_type}")
            return []
    
    # ANCHOR: Specific Cascading Implementations
    def _cascade_main_relation(self, target_artifact: pd.Series, artifacts_df: pd.DataFrame,
                             columns_df: pd.DataFrame, stages_df: pd.DataFrame) -> List[Dict]:
        """
        Handle 'main' upstream relationship cascading.
        
        Logic:
        - Take all fields from upstream node except partition fields
        - Add technical fields of the stage at the end
        - Include CDC module fields
        - Name fields based on source or business side
        - Change data types if platform changes
        - For dimensions: create SK and BK fields
        """
        new_columns = []
        
        # Find upstream artifact
        upstream_artifacts = self._find_upstream_artifacts(target_artifact, artifacts_df)
        if not upstream_artifacts:
            return new_columns
        
        target_stage = target_artifact['stage_name']
        target_platform = self._get_stage_platform(target_stage, stages_df)
        
        for upstream_artifact in upstream_artifacts:
            # Get upstream columns (excluding partition fields)
            upstream_columns = self._get_upstream_columns(upstream_artifact['artifact_id'], columns_df, exclude_partition=True)
            
            # Add main columns with potential data type conversion
            for col in upstream_columns:
                new_col = self._create_cascaded_column(
                    col, target_artifact, target_stage, target_platform, stages_df
                )
                new_columns.append(new_col)
            
            # Add dimension SK/BK fields if target is dimension
            if self._is_dimension_artifact(target_artifact):
                sk_col, bk_col = self._create_dimension_keys(upstream_artifact, target_artifact, target_platform)
                new_columns.extend([sk_col, bk_col])
            
            # Add CDC field
            cdc_col = self._create_cdc_column(upstream_artifact, target_artifact, target_platform)
            new_columns.append(cdc_col)
        
        # Add technical columns for the stage
        tech_columns = self._create_technical_columns(target_stage, target_artifact, target_platform)
        new_columns.extend(tech_columns)
        
        return new_columns
    
    def _cascade_get_key_relation(self, target_artifact: pd.Series, artifacts_df: pd.DataFrame,
                                columns_df: pd.DataFrame, stages_df: pd.DataFrame) -> List[Dict]:
        """
        Handle 'get_key' upstream relationship cascading.
        
        Logic (only for fact tables in gold stage):
        - Create SK fields (ordinal 1-20)
        - Create BK fields (ordinal 21-40)  
        - Get first 3 fields of upstream node
        - Name fields based on source or business side
        - Change data types if platform changes
        """
        new_columns = []
        
        # Only apply to fact tables in gold stage
        if target_artifact['stage_name'].lower() != 'gold':
            return new_columns
        
        # Find upstream artifacts
        upstream_artifacts = self._find_upstream_artifacts(target_artifact, artifacts_df)
        if not upstream_artifacts:
            return new_columns
        
        target_platform = self._get_stage_platform(target_artifact['stage_name'], stages_df)
        ordinal_sk = 1
        ordinal_bk = 21
        
        for upstream_artifact in upstream_artifacts:
            # Create SK and BK fields for dimensions
            if self._is_dimension_artifact(upstream_artifact):
                sk_col = self._create_dimension_key_field(
                    upstream_artifact, target_artifact, target_platform, 'SK', ordinal_sk
                )
                bk_col = self._create_dimension_key_field(
                    upstream_artifact, target_artifact, target_platform, 'BK', ordinal_bk
                )
                new_columns.extend([sk_col, bk_col])
                ordinal_sk += 1
                ordinal_bk += 1
            
            # Get first 3 fields of upstream node
            upstream_columns = self._get_upstream_columns(upstream_artifact['artifact_id'], columns_df, limit=3)
            for col in upstream_columns:
                new_col = self._create_cascaded_column(
                    col, target_artifact, target_artifact['stage_name'], target_platform, stages_df
                )
                new_columns.append(new_col)
        
        return new_columns
    
    def _cascade_lookup_relation(self, target_artifact: pd.Series, artifacts_df: pd.DataFrame,
                               columns_df: pd.DataFrame, stages_df: pd.DataFrame) -> List[Dict]:
        """
        Handle 'lookup' upstream relationship cascading.
        
        Logic:
        - Get first 3 fields of upstream node
        - Name fields based on source or business side
        - Change data types if platform changes
        """
        new_columns = []
        
        # Find upstream artifacts
        upstream_artifacts = self._find_upstream_artifacts(target_artifact, artifacts_df)
        if not upstream_artifacts:
            return new_columns
        
        target_platform = self._get_stage_platform(target_artifact['stage_name'], stages_df)
        
        for upstream_artifact in upstream_artifacts:
            # Get first 3 fields of upstream node
            upstream_columns = self._get_upstream_columns(upstream_artifact['artifact_id'], columns_df, limit=3)
            
            for col in upstream_columns:
                new_col = self._create_cascaded_column(
                    col, target_artifact, target_artifact['stage_name'], target_platform, stages_df
                )
                new_columns.append(new_col)
        
        return new_columns
    
    def _cascade_pbi_relation(self, target_artifact: pd.Series, artifacts_df: pd.DataFrame,
                            columns_df: pd.DataFrame, stages_df: pd.DataFrame) -> List[Dict]:
        """
        Handle 'pbi' upstream relationship cascading.
        
        Logic:
        - No impact on cascading (returns empty list)
        """
        self.logger.info(f"PBI relation has no cascading impact for artifact {target_artifact['artifact_id']}")
        return []
    
    # ANCHOR: Helper Methods
    def _find_upstream_artifacts(self, target_artifact: pd.Series, artifacts_df: pd.DataFrame) -> List[pd.Series]:
        """Find upstream artifacts for the target artifact."""
        upstream_artifacts = []
        
        # Get upstream artifact IDs (assuming comma-separated in Upstream Artifact column)
        upstream_ids_str = target_artifact.get('Upstream Artifact', '')
        if not upstream_ids_str:
            return upstream_artifacts
        
        try:
            upstream_ids = [id.strip() for id in str(upstream_ids_str).split(',') if id.strip()]
            
            for upstream_id in upstream_ids:
                upstream_artifact = artifacts_df[artifacts_df['artifact_id'] == upstream_id]
                if not upstream_artifact.empty:
                    upstream_artifacts.append(upstream_artifact.iloc[0])
                    
        except Exception as e:
            self.logger.warning(f"Error parsing upstream artifacts: {str(e)}")
        
        return upstream_artifacts
    
    def _get_upstream_columns(self, artifact_id: str, columns_df: pd.DataFrame, 
                            exclude_partition: bool = False, limit: int = None) -> List[pd.Series]:
        """Get columns for an upstream artifact."""
        artifact_columns = columns_df[columns_df['artifact_id'] == artifact_id]
        
        if exclude_partition:
            # Exclude partition fields (containing 'Partition' in name)
            artifact_columns = artifact_columns[
                ~artifact_columns['column_name'].str.contains('Partition', case=False, na=False)
            ]
        
        # Sort by order if available
        if 'order' in artifact_columns.columns:
            artifact_columns = artifact_columns.sort_values('order')
        
        # Apply limit if specified
        if limit:
            artifact_columns = artifact_columns.head(limit)
        
        return [row for _, row in artifact_columns.iterrows()]
    
    def _create_cascaded_column(self, source_col: pd.Series, target_artifact: pd.Series,
                              target_stage: str, target_platform: str, stages_df: pd.DataFrame) -> Dict:
        """Create a cascaded column with appropriate naming and data type conversion."""
        # Get source platform
        source_stage = self._get_column_stage(source_col, stages_df)
        source_platform = self._get_stage_platform(source_stage, stages_df)
        
        # Convert data type if platform changes
        source_data_type = source_col.get('data_type', '')
        target_data_type = self._convert_data_type(source_data_type, target_platform)
        
        # Determine naming strategy based on stage side
        target_stage_info = self._get_stage_info(target_stage, stages_df)
        naming_side = target_stage_info.get('Source or Business Side', 'business')
        
        # Generate column name
        column_name = self._generate_column_name(source_col, naming_side)
        
        # Get next column ID and order
        next_id = self._get_next_column_id()
        next_order = self._get_next_column_order(target_artifact['artifact_id'])
        
        return {
            'column_id': next_id,
            'column_name': column_name,
            'artifact_id': target_artifact['artifact_id'],
            'data_type': target_data_type,
            'column_business_name': self._generate_business_name(column_name),
            'column_comment': f"Cascaded from {source_col.get('column_name', '')}",
            'order': next_order,
            'source_column': source_col.get('column_name', ''),
            'cascaded': True
        }
    
    def _create_dimension_keys(self, upstream_artifact: pd.Series, target_artifact: pd.Series, 
                             target_platform: str) -> Tuple[Dict, Dict]:
        """Create SK and BK fields for dimension cascading."""
        upstream_name = upstream_artifact['Artifact Name']
        
        # Create SK field
        sk_col = {
            'column_id': self._get_next_column_id(),
            'column_name': f'dim_{upstream_name}_SK',
            'artifact_id': target_artifact['artifact_id'],
            'data_type': 'BIGINT',
            'column_business_name': f'dim_{upstream_name}_surrogate_key',
            'column_comment': f'Surrogate key for {upstream_name} dimension',
            'order': 1,
            'source_column': f'{upstream_name}_SK',
            'cascaded': True
        }
        
        # Create BK field
        bk_col = {
            'column_id': self._get_next_column_id(),
            'column_name': f'dim_{upstream_name}_BK',
            'artifact_id': target_artifact['artifact_id'],
            'data_type': 'BIGINT',
            'column_business_name': f'dim_{upstream_name}_business_key',
            'column_comment': f'Business key for {upstream_name} dimension',
            'order': 2,
            'source_column': f'{upstream_name}_BK',
            'cascaded': True
        }
        
        return sk_col, bk_col
    
    def _create_cdc_column(self, upstream_artifact: pd.Series, target_artifact: pd.Series, 
                         target_platform: str) -> Dict:
        """Create CDC (Change Data Capture) column."""
        upstream_stage = upstream_artifact['stage_name']
        cdc_column_name = f'__{upstream_stage}_last_changed_DT'
        
        return {
            'column_id': self._get_next_column_id(),
            'column_name': cdc_column_name,
            'artifact_id': target_artifact['artifact_id'],
            'data_type': 'TIMESTAMP',
            'column_business_name': f'{upstream_stage}_last_changed_date',
            'column_comment': f'CDC timestamp from {upstream_stage} stage',
            'order': self._get_next_column_order(target_artifact['artifact_id']),
            'source_column': cdc_column_name,
            'cascaded': True
        }
    
    def _create_technical_columns(self, stage: str, target_artifact: pd.Series, 
                                target_platform: str) -> List[Dict]:
        """Create technical columns for the stage."""
        tech_columns = []
        
        # Get technical columns configuration for this stage
        tech_fields = self._get_technical_fields_for_stage(stage)
        
        for tech_col_config in tech_fields:
            # Only add fields that are marked for inclusion
            if not tech_col_config.get('include_in_tech_fields', False):
                tech_col = {
                    'column_id': self._get_next_column_id(),
                    'column_name': tech_col_config['column_name'],
                    'artifact_id': target_artifact['artifact_id'],
                    'data_type': tech_col_config['data_type'],
                    'column_business_name': tech_col_config['column_name'].lower(),
                    'column_comment': f'Technical column for {stage} stage',
                    'order': self._get_next_column_order(target_artifact['artifact_id']),
                    'source_column': tech_col_config['column_name'],
                    'cascaded': True
                }
                tech_columns.append(tech_col)
        
        return tech_columns
    
    # ANCHOR: Utility Methods
    def _remove_duplicate_columns(self, new_columns: List[Dict], existing_columns_df: pd.DataFrame, artifact_id: str) -> List[Dict]:
        """
        Remove columns that would create duplicates within the same artifact.
        
        Args:
            new_columns: List of new columns to add
            existing_columns_df: DataFrame of existing columns
            artifact_id: ID of the target artifact
            
        Returns:
            List[Dict]: Filtered list without duplicates
        """
        # Get existing column names for this artifact
        existing_artifact_columns = existing_columns_df[existing_columns_df['artifact_id'] == artifact_id]
        existing_column_names = set(existing_artifact_columns['column_name'].tolist())
        
        # Track new column names to prevent duplicates within the new columns themselves
        new_column_names = set()
        filtered_columns = []
        
        for new_col in new_columns:
            col_name = new_col.get('column_name', '')
            
            # Skip if column name already exists in artifact or in new columns
            if col_name in existing_column_names or col_name in new_column_names:
                continue
                
            # Add to filtered list and track the name
            filtered_columns.append(new_col)
            new_column_names.add(col_name)
        
        return filtered_columns

    def _get_stage_platform(self, stage_name: str, stages_df: pd.DataFrame) -> str:
        """Get platform for a stage."""
        stage_row = stages_df[stages_df['stage_name'] == stage_name]
        if not stage_row.empty:
            return stage_row.iloc[0].get('platform', 'SQL Server')
        return 'SQL Server'
    
    def _get_stage_info(self, stage_name: str, stages_df: pd.DataFrame) -> Dict:
        """Get stage information."""
        stage_row = stages_df[stages_df['stage_name'] == stage_name]
        if not stage_row.empty:
            return stage_row.iloc[0].to_dict()
        return {}
    
    def _is_dimension_artifact(self, artifact: pd.Series) -> bool:
        """Check if artifact is a dimension."""
        artifact_name = artifact.get('Artifact Name', '').lower()
        return 'dim' in artifact_name or 'dimension' in artifact_name
    
    def _generate_column_name(self, source_col: pd.Series, naming_side: str) -> str:
        """Generate column name based on naming strategy."""
        source_name = source_col.get('column_name', '')
        
        if naming_side.lower() == 'business':
            # Use business-friendly naming
            business_name = source_col.get('Column Business Name', '')
            return business_name if business_name else source_name
        else:
            # Use source naming
            return source_name
    
    def _generate_business_name(self, column_name: str) -> str:
        """Generate business-friendly name from column name."""
        # Simple transformation: replace underscores with spaces and title case
        return column_name.replace('_', ' ').title().replace(' ', '_').lower()
    
    def _get_next_column_id(self) -> str:
        """Get next available globally unique column ID."""
        if self._global_column_id_counter is None:
            # Start fresh - find the highest existing ID and continue from there
            try:
                columns_df = self.excel_utils.read_sheet_data(self.workbook_path, 'Columns')
                max_id = 0
                if not columns_df.empty and 'Column ID' in columns_df.columns:
                    # Extract numeric parts from existing IDs (format: c1, c2, c3, etc.)
                    for col_id in columns_df['Column ID']:
                        if isinstance(col_id, str) and col_id.startswith('c'):
                            try:
                                numeric_part = int(col_id[1:])
                                max_id = max(max_id, numeric_part)
                            except ValueError:
                                continue
                # Start from the next available number
                self._global_column_id_counter = max_id
            except Exception:
                # If we can't read existing data, start from 0
                self._global_column_id_counter = 0
        
        # Generate next unique ID
        self._global_column_id_counter += 1
        return f"c{self._global_column_id_counter}"
    
    def _get_next_column_order(self, artifact_id: str) -> int:
        """Get next order number for columns in an artifact."""
        try:
            columns_df = self.excel_utils.read_sheet_data(self.workbook_path, 'Columns')
            if not columns_df.empty and 'artifact_id' in columns_df.columns and 'order' in columns_df.columns:
                artifact_columns = columns_df[columns_df['artifact_id'] == artifact_id]
                if not artifact_columns.empty:
                    max_order = artifact_columns['order'].max()
                    return max_order + 1 if pd.notna(max_order) else 1
            return 1
        except Exception:
            return 1
    
    def _reorder_columns_by_hierarchy(self, columns_list: list) -> list:
        """
        Reorder columns according to hierarchy: SK -> BK -> attributes -> technical fields.
        Updates the Order field for each column.
        """
        if not columns_list:
            return columns_list
        
        # Sort columns by type priority, then by original order (stable sort)
        sorted_columns = sorted(columns_list, key=lambda col: (
            self._get_column_type_order_priority(
                col.get('Column Group', ''), 
                col.get('column_name', '')
            ),
            col.get('order', 999)  # Use original order as secondary sort
        ))
        
        # Update order field to reflect new hierarchy
        for i, column in enumerate(sorted_columns, 1):
            column['order'] = i
        
        return sorted_columns
    
    def _get_column_type_order_priority(self, column_group: str, column_name: str) -> int:
        """
        Get ordering priority for column based on type.
        Lower numbers come first. 
        Priority: Primary Key (0) -> SK (1) -> BK (2) -> Regular attributes (3) -> Technical fields (4)
        """
        if not column_group or pd.isna(column_group):
            # Use column name patterns for fallback detection
            if column_name and isinstance(column_name, str):
                if column_name.endswith('_SK'):
                    return 1  # SKs first
                elif column_name.endswith('_BK'):
                    return 2  # BKs second
                elif column_name.startswith('__') or 'lastChanged' in column_name or 'gold' in column_name:
                    return 4  # Technical fields last
            return 3  # Regular attributes in middle
        
        column_group_lower = str(column_group).lower()
        
        if column_group_lower in ['primary_key', 'primarykey', 'pk']:
            return 0  # Primary keys first (highest priority)
        elif column_group_lower == 'sks':
            return 1  # SKs second
        elif column_group_lower == 'bks':
            return 2  # BKs third  
        elif column_group_lower in ['technical_fields', 'technical fields']:
            return 4  # Technical fields last
        else:
            return 3  # Regular attributes in middle
    
    def _get_column_stage(self, column: pd.Series, stages_df: pd.DataFrame) -> str:
        """Get stage name for a column."""
        # This needs to be implemented based on how stages are linked to columns
        return 'bronze'  # Placeholder
    
    def _add_columns_to_dataframe(self, columns_df: pd.DataFrame, new_columns: List[Dict]) -> pd.DataFrame:
        """Add new columns to the columns DataFrame."""
        if not new_columns:
            return columns_df
        
        new_columns_df = pd.DataFrame(new_columns)
        return pd.concat([columns_df, new_columns_df], ignore_index=True)
    
    # ANCHOR: Configuration Management
    def create_cascading_config_file(self) -> bool:
        """Create the latest cascading configuration file with enhanced structure."""
        try:
            # Enhanced configuration with updated structure for enhanced relation processing
            sheets_config = {
                'DataTypeMappings': {
                    'headers': ['Source_Data_Type', 'SQL_Server_Data_Type', 'Databricks_SQL_Data_Type', 'Power_BI_Data_Type', 'Notes'],
                    'default_data': self._create_enhanced_data_type_mappings()
                },
                'TechnicalColumns': {
                    'headers': ['Stage_ID', 'Stage_Name', 'Column_Name', 'Data_Type', 'include_in_tech_fields', 'Take_To_Next_Level', 'Artifact_Type_Specific', 'Description'],
                    'default_data': self._create_enhanced_technical_columns()
                },
                'StageConfiguration': {
                    'headers': ['Stage_ID', 'Stage_Name', 'Platform', 'Artifact_Side', 'Processing_Notes'],
                    'default_data': self._create_stage_configuration()
                },
                'RelationTypes': {
                    'headers': ['Relation_Type', 'Description', 'Processing_Logic', 'Field_Limit', 'Use_Cases'],
                    'default_data': self._create_relation_types_config()
                }
            }
            
            success = self.excel_utils.create_workbook_with_sheets(self.config_path, sheets_config)
            
            if success:
                self.logger.info(f"Created enhanced cascading configuration file: {self.config_path}")
                return True
            else:
                self.logger.error("Failed to create cascading configuration file")
                return False
                
        except Exception as e:
            self.logger.error(f"Error creating cascading configuration file: {str(e)}")
            return False

    def _create_enhanced_data_type_mappings(self) -> List[Dict]:
        """Create enhanced data type mappings with all platforms."""
        mappings = [
            # Numeric Types
            {"Source_Data_Type": "INT", "SQL_Server_Data_Type": "INT", "Databricks_SQL_Data_Type": "INT", "Power_BI_Data_Type": "INT64", "Notes": "Standard integer"},
            {"Source_Data_Type": "BIGINT", "SQL_Server_Data_Type": "BIGINT", "Databricks_SQL_Data_Type": "BIGINT", "Power_BI_Data_Type": "INT64", "Notes": "Large integer"},
            {"Source_Data_Type": "SMALLINT", "SQL_Server_Data_Type": "SMALLINT", "Databricks_SQL_Data_Type": "SMALLINT", "Power_BI_Data_Type": "INT64", "Notes": "Small integer"},
            {"Source_Data_Type": "TINYINT", "SQL_Server_Data_Type": "TINYINT", "Databricks_SQL_Data_Type": "TINYINT", "Power_BI_Data_Type": "INT64", "Notes": "Tiny integer"},
            {"Source_Data_Type": "BIT", "SQL_Server_Data_Type": "BIT", "Databricks_SQL_Data_Type": "BOOLEAN", "Power_BI_Data_Type": "Boolean", "Notes": "Boolean flag"},
            {"Source_Data_Type": "DECIMAL", "SQL_Server_Data_Type": "DECIMAL(18,2)", "Databricks_SQL_Data_Type": "DECIMAL(18,2)", "Power_BI_Data_Type": "Decimal", "Notes": "Precise decimal"},
            {"Source_Data_Type": "NUMERIC", "SQL_Server_Data_Type": "NUMERIC(18,2)", "Databricks_SQL_Data_Type": "NUMERIC(18,2)", "Power_BI_Data_Type": "Decimal", "Notes": "Numeric with precision"},
            {"Source_Data_Type": "FLOAT", "SQL_Server_Data_Type": "FLOAT", "Databricks_SQL_Data_Type": "FLOAT", "Power_BI_Data_Type": "Double", "Notes": "Floating point"},
            {"Source_Data_Type": "REAL", "SQL_Server_Data_Type": "REAL", "Databricks_SQL_Data_Type": "REAL", "Power_BI_Data_Type": "Double", "Notes": "Real number"},
            {"Source_Data_Type": "MONEY", "SQL_Server_Data_Type": "MONEY", "Databricks_SQL_Data_Type": "DECIMAL(19,4)", "Power_BI_Data_Type": "Decimal", "Notes": "Currency values"},
            
            # String Types
            {"Source_Data_Type": "CHAR", "SQL_Server_Data_Type": "CHAR(255)", "Databricks_SQL_Data_Type": "CHAR(255)", "Power_BI_Data_Type": "String", "Notes": "Fixed length char"},
            {"Source_Data_Type": "VARCHAR", "SQL_Server_Data_Type": "VARCHAR(MAX)", "Databricks_SQL_Data_Type": "STRING", "Power_BI_Data_Type": "String", "Notes": "Variable length string"},
            {"Source_Data_Type": "TEXT", "SQL_Server_Data_Type": "NVARCHAR(MAX)", "Databricks_SQL_Data_Type": "STRING", "Power_BI_Data_Type": "String", "Notes": "Large text"},
            {"Source_Data_Type": "NCHAR", "SQL_Server_Data_Type": "NCHAR(255)", "Databricks_SQL_Data_Type": "STRING", "Power_BI_Data_Type": "String", "Notes": "Unicode fixed char"},
            {"Source_Data_Type": "NVARCHAR", "SQL_Server_Data_Type": "NVARCHAR(MAX)", "Databricks_SQL_Data_Type": "STRING", "Power_BI_Data_Type": "String", "Notes": "Unicode variable string"},
            {"Source_Data_Type": "NTEXT", "SQL_Server_Data_Type": "NVARCHAR(MAX)", "Databricks_SQL_Data_Type": "STRING", "Power_BI_Data_Type": "String", "Notes": "Unicode large text"},
            
            # Date/Time Types
            {"Source_Data_Type": "DATE", "SQL_Server_Data_Type": "DATE", "Databricks_SQL_Data_Type": "DATE", "Power_BI_Data_Type": "Date", "Notes": "Date only"},
            {"Source_Data_Type": "DATETIME", "SQL_Server_Data_Type": "DATETIME", "Databricks_SQL_Data_Type": "TIMESTAMP", "Power_BI_Data_Type": "DateTime", "Notes": "Date and time"},
            {"Source_Data_Type": "DATETIME2", "SQL_Server_Data_Type": "DATETIME2", "Databricks_SQL_Data_Type": "TIMESTAMP", "Power_BI_Data_Type": "DateTime", "Notes": "Enhanced datetime"},
            {"Source_Data_Type": "SMALLDATETIME", "SQL_Server_Data_Type": "SMALLDATETIME", "Databricks_SQL_Data_Type": "TIMESTAMP", "Power_BI_Data_Type": "DateTime", "Notes": "Small datetime"},
            {"Source_Data_Type": "TIME", "SQL_Server_Data_Type": "TIME", "Databricks_SQL_Data_Type": "TIME", "Power_BI_Data_Type": "Time", "Notes": "Time only"},
            {"Source_Data_Type": "TIMESTAMP", "SQL_Server_Data_Type": "DATETIME2", "Databricks_SQL_Data_Type": "TIMESTAMP", "Power_BI_Data_Type": "DateTime", "Notes": "Timestamp"},
            
            # Binary Types  
            {"Source_Data_Type": "BINARY", "SQL_Server_Data_Type": "BINARY(8000)", "Databricks_SQL_Data_Type": "BINARY", "Power_BI_Data_Type": "Binary", "Notes": "Fixed binary"},
            {"Source_Data_Type": "VARBINARY", "SQL_Server_Data_Type": "VARBINARY(MAX)", "Databricks_SQL_Data_Type": "BINARY", "Power_BI_Data_Type": "Binary", "Notes": "Variable binary"},
            {"Source_Data_Type": "IMAGE", "SQL_Server_Data_Type": "VARBINARY(MAX)", "Databricks_SQL_Data_Type": "BINARY", "Power_BI_Data_Type": "Binary", "Notes": "Image/blob data"},
            
            # Special Types
            {"Source_Data_Type": "UNIQUEIDENTIFIER", "SQL_Server_Data_Type": "UNIQUEIDENTIFIER", "Databricks_SQL_Data_Type": "STRING", "Power_BI_Data_Type": "String", "Notes": "GUID/UUID"},
            {"Source_Data_Type": "XML", "SQL_Server_Data_Type": "XML", "Databricks_SQL_Data_Type": "STRING", "Power_BI_Data_Type": "String", "Notes": "XML data"},
            {"Source_Data_Type": "JSON", "SQL_Server_Data_Type": "NVARCHAR(MAX)", "Databricks_SQL_Data_Type": "STRING", "Power_BI_Data_Type": "String", "Notes": "JSON data"}
        ]
        return mappings

    def _create_enhanced_technical_columns(self) -> List[Dict]:
        """Create enhanced technical columns configuration using the ACTUAL column names from the original config."""
        columns = [
            # Bronze stage technical fields (using original naming)
            {"Stage_ID": "s1", "Stage_Name": "bronze", "Column_Name": "__SourceSystem", "Data_Type": "STRING", "include_in_tech_fields": False, "Take_To_Next_Level": True, "Artifact_Type_Specific": "all", "Description": "Source system identifier"},
            {"Stage_ID": "s1", "Stage_Name": "bronze", "Column_Name": "__SourceFileName", "Data_Type": "STRING", "include_in_tech_fields": False, "Take_To_Next_Level": True, "Artifact_Type_Specific": "all", "Description": "Original source file name"},
            {"Stage_ID": "s1", "Stage_Name": "bronze", "Column_Name": "__SourceFilePath", "Data_Type": "STRING", "include_in_tech_fields": False, "Take_To_Next_Level": True, "Artifact_Type_Specific": "all", "Description": "Source file path"},
            {"Stage_ID": "s1", "Stage_Name": "bronze", "Column_Name": "__bronze_insertDT", "Data_Type": "TIMESTAMP", "include_in_tech_fields": False, "Take_To_Next_Level": True, "Artifact_Type_Specific": "all", "Description": "Bronze insertion timestamp"},
            {"Stage_ID": "s1", "Stage_Name": "bronze", "Column_Name": "__bronzePartition_InsertYear", "Data_Type": "INT", "include_in_tech_fields": False, "Take_To_Next_Level": False, "Artifact_Type_Specific": "all", "Description": "Partition year for bronze data"},
            {"Stage_ID": "s1", "Stage_Name": "bronze", "Column_Name": "__bronzePartition_InsertMonth", "Data_Type": "INT", "include_in_tech_fields": False, "Take_To_Next_Level": False, "Artifact_Type_Specific": "all", "Description": "Partition month for bronze data"},
            {"Stage_ID": "s1", "Stage_Name": "bronze", "Column_Name": "__bronzePartition_insertDate", "Data_Type": "INT", "include_in_tech_fields": False, "Take_To_Next_Level": False, "Artifact_Type_Specific": "all", "Description": "Partition date for bronze data"},
            {"Stage_ID": "s1", "Stage_Name": "bronze", "Column_Name": "__bronze_hash", "Data_Type": "STRING", "include_in_tech_fields": True, "Take_To_Next_Level": False, "Artifact_Type_Specific": "all", "Description": "Data hash for change detection"},
            {"Stage_ID": "s1", "Stage_Name": "bronze", "Column_Name": "__bronze_status", "Data_Type": "STRING", "include_in_tech_fields": True, "Take_To_Next_Level": False, "Artifact_Type_Specific": "all", "Description": "Processing status"},
            
            # Silver stage technical fields (using original naming)
            {"Stage_ID": "s2", "Stage_Name": "silver", "Column_Name": "__silver_lastChanged_DT", "Data_Type": "TIMESTAMP", "include_in_tech_fields": False, "Take_To_Next_Level": True, "Artifact_Type_Specific": "all", "Description": "Silver last changed timestamp"},
            {"Stage_ID": "s2", "Stage_Name": "silver", "Column_Name": "__silverPartition_xxxYear", "Data_Type": "INT", "include_in_tech_fields": True, "Take_To_Next_Level": False, "Artifact_Type_Specific": "all", "Description": "Silver partition year (xxx = business date field)"},
            {"Stage_ID": "s2", "Stage_Name": "silver", "Column_Name": "__silverPartition_xxxMonth", "Data_Type": "INT", "include_in_tech_fields": True, "Take_To_Next_Level": False, "Artifact_Type_Specific": "all", "Description": "Silver partition month (xxx = business date field)"},
            {"Stage_ID": "s2", "Stage_Name": "silver", "Column_Name": "__silverPartition_xxxDate", "Data_Type": "INT", "include_in_tech_fields": True, "Take_To_Next_Level": False, "Artifact_Type_Specific": "all", "Description": "Silver partition date (xxx = business date field)"},
            {"Stage_ID": "s2", "Stage_Name": "silver", "Column_Name": "__silver_validFrom", "Data_Type": "TIMESTAMP", "include_in_tech_fields": True, "Take_To_Next_Level": True, "Artifact_Type_Specific": "dimension", "Description": "Valid from timestamp for SCD Type 2"},
            {"Stage_ID": "s2", "Stage_Name": "silver", "Column_Name": "__silver_validTo", "Data_Type": "TIMESTAMP", "include_in_tech_fields": True, "Take_To_Next_Level": True, "Artifact_Type_Specific": "dimension", "Description": "Valid to timestamp for SCD Type 2"},
            {"Stage_ID": "s2", "Stage_Name": "silver", "Column_Name": "__silver_isCurrent", "Data_Type": "BOOLEAN", "include_in_tech_fields": True, "Take_To_Next_Level": True, "Artifact_Type_Specific": "dimension", "Description": "Current record flag for SCD Type 2"},
            {"Stage_ID": "s2", "Stage_Name": "silver", "Column_Name": "__silver_hash", "Data_Type": "STRING", "include_in_tech_fields": True, "Take_To_Next_Level": False, "Artifact_Type_Specific": "all", "Description": "Data hash for change detection"},
            
            # Gold stage technical fields (using original naming)
            {"Stage_ID": "s3", "Stage_Name": "gold", "Column_Name": "__gold_lastChanged_DT", "Data_Type": "TIMESTAMP", "include_in_tech_fields": False, "Take_To_Next_Level": True, "Artifact_Type_Specific": "all", "Description": "Gold last changed timestamp"},
            {"Stage_ID": "s3", "Stage_Name": "gold", "Column_Name": "__goldPartition_XXXYear", "Data_Type": "INT", "include_in_tech_fields": True, "Take_To_Next_Level": False, "Artifact_Type_Specific": "all", "Description": "Gold partition year (XXX = business date field)"},
            {"Stage_ID": "s3", "Stage_Name": "gold", "Column_Name": "__goldPartition_XXXMonth", "Data_Type": "INT", "include_in_tech_fields": True, "Take_To_Next_Level": False, "Artifact_Type_Specific": "all", "Description": "Gold partition month (XXX = business date field)"},
            {"Stage_ID": "s3", "Stage_Name": "gold", "Column_Name": "__goldPartition_XXXDate", "Data_Type": "INT", "include_in_tech_fields": True, "Take_To_Next_Level": False, "Artifact_Type_Specific": "all", "Description": "Gold partition date (XXX = business date field)"},
            {"Stage_ID": "s3", "Stage_Name": "gold", "Column_Name": "__gold_aggregation_level", "Data_Type": "STRING", "include_in_tech_fields": True, "Take_To_Next_Level": True, "Artifact_Type_Specific": "fact", "Description": "Aggregation level for fact tables"},
            {"Stage_ID": "s3", "Stage_Name": "gold", "Column_Name": "__gold_measure_type", "Data_Type": "STRING", "include_in_tech_fields": True, "Take_To_Next_Level": True, "Artifact_Type_Specific": "fact", "Description": "Measure type classification"},
            {"Stage_ID": "s3", "Stage_Name": "gold", "Column_Name": "__gold_quality_score", "Data_Type": "DECIMAL", "include_in_tech_fields": True, "Take_To_Next_Level": False, "Artifact_Type_Specific": "all", "Description": "Data quality score"},
            
            # Audit fields for bronze stage
            {"Stage_ID": "s1", "Stage_Name": "bronze", "Column_Name": "__audit_created_by", "Data_Type": "STRING", "include_in_tech_fields": True, "Take_To_Next_Level": True, "Artifact_Type_Specific": "all", "Description": "Created by user/process"},
            {"Stage_ID": "s1", "Stage_Name": "bronze", "Column_Name": "__audit_created_date", "Data_Type": "TIMESTAMP", "include_in_tech_fields": True, "Take_To_Next_Level": True, "Artifact_Type_Specific": "all", "Description": "Created date"},
            {"Stage_ID": "s1", "Stage_Name": "bronze", "Column_Name": "__audit_modified_by", "Data_Type": "STRING", "include_in_tech_fields": True, "Take_To_Next_Level": True, "Artifact_Type_Specific": "all", "Description": "Modified by user/process"},
            {"Stage_ID": "s1", "Stage_Name": "bronze", "Column_Name": "__audit_modified_date", "Data_Type": "TIMESTAMP", "include_in_tech_fields": True, "Take_To_Next_Level": True, "Artifact_Type_Specific": "all", "Description": "Modified date"},
            
            # Audit fields for silver stage
            {"Stage_ID": "s2", "Stage_Name": "silver", "Column_Name": "__audit_created_by", "Data_Type": "STRING", "include_in_tech_fields": True, "Take_To_Next_Level": True, "Artifact_Type_Specific": "all", "Description": "Created by user/process"},
            {"Stage_ID": "s2", "Stage_Name": "silver", "Column_Name": "__audit_created_date", "Data_Type": "TIMESTAMP", "include_in_tech_fields": True, "Take_To_Next_Level": True, "Artifact_Type_Specific": "all", "Description": "Created date"},
            {"Stage_ID": "s2", "Stage_Name": "silver", "Column_Name": "__audit_modified_by", "Data_Type": "STRING", "include_in_tech_fields": True, "Take_To_Next_Level": True, "Artifact_Type_Specific": "all", "Description": "Modified by user/process"},
            {"Stage_ID": "s2", "Stage_Name": "silver", "Column_Name": "__audit_modified_date", "Data_Type": "TIMESTAMP", "include_in_tech_fields": True, "Take_To_Next_Level": True, "Artifact_Type_Specific": "all", "Description": "Modified date"},
            
            # Audit fields for gold stage
            {"Stage_ID": "s3", "Stage_Name": "gold", "Column_Name": "__audit_created_by", "Data_Type": "STRING", "include_in_tech_fields": True, "Take_To_Next_Level": True, "Artifact_Type_Specific": "all", "Description": "Created by user/process"},
            {"Stage_ID": "s3", "Stage_Name": "gold", "Column_Name": "__audit_created_date", "Data_Type": "TIMESTAMP", "include_in_tech_fields": True, "Take_To_Next_Level": True, "Artifact_Type_Specific": "all", "Description": "Created date"},
            {"Stage_ID": "s3", "Stage_Name": "gold", "Column_Name": "__audit_modified_by", "Data_Type": "STRING", "include_in_tech_fields": True, "Take_To_Next_Level": True, "Artifact_Type_Specific": "all", "Description": "Modified by user/process"},
            {"Stage_ID": "s3", "Stage_Name": "gold", "Column_Name": "__audit_modified_date", "Data_Type": "TIMESTAMP", "include_in_tech_fields": True, "Take_To_Next_Level": True, "Artifact_Type_Specific": "all", "Description": "Modified date"}
        ]
        return columns

    def _create_stage_configuration(self) -> List[Dict]:
        """Create stage configuration for enhanced processing."""
        stages = [
            {"Stage_ID": "s0", "Stage_Name": "0_drop_zone", "Platform": "Azure SQL", "Artifact_Side": "source", "Processing_Notes": "Raw data ingestion, minimal processing"},
            {"Stage_ID": "s1", "Stage_Name": "1_bronze", "Platform": "Azure SQL", "Artifact_Side": "source", "Processing_Notes": "Raw storage with basic structure"},
            {"Stage_ID": "s2", "Stage_Name": "2_silver", "Platform": "Azure SQL", "Artifact_Side": "business", "Processing_Notes": "Cleaned and validated, SCD implementation"},
            {"Stage_ID": "s3", "Stage_Name": "3_gold", "Platform": "Azure SQL", "Artifact_Side": "business", "Processing_Notes": "Business ready, conformed dimensions"},
            {"Stage_ID": "s4", "Stage_Name": "4_mart", "Platform": "Azure SQL", "Artifact_Side": "business", "Processing_Notes": "Analytical marts and aggregations"},
            {"Stage_ID": "s5", "Stage_Name": "5_PBI_Model", "Platform": "Power BI", "Artifact_Side": "business", "Processing_Notes": "Power BI optimized model"},
            {"Stage_ID": "s6", "Stage_Name": "6_PBI_Reports", "Platform": "Power BI", "Artifact_Side": "business", "Processing_Notes": "Report layer definitions"}
        ]
        return stages

    def _create_relation_types_config(self) -> List[Dict]:
        """Create relation types configuration for enhanced processing."""
        relations = [
            {
                "Relation_Type": "main", 
                "Description": "Full column propagation with technical fields", 
                "Processing_Logic": "Context-aware processing based on artifact type and stage transition", 
                "Field_Limit": "No limit", 
                "Use_Cases": "Standard column cascading between stages"
            },
            {
                "Relation_Type": "get_key", 
                "Description": "Dimension key propagation for fact tables", 
                "Processing_Logic": "Extracts surrogate keys (SKs) and business keys (BKs) only", 
                "Field_Limit": "Keys only", 
                "Use_Cases": "Foreign key relationships in fact tables"
            },
            {
                "Relation_Type": "lookup", 
                "Description": "Limited column lookup with priority-based selection", 
                "Processing_Logic": "Priority order: SKs → BKs → Attributes, configurable limit", 
                "Field_Limit": "3 (default)", 
                "Use_Cases": "Reference lookups and denormalization"
            },
            {
                "Relation_Type": "pbi", 
                "Description": "Power BI specific minimal cascading", 
                "Processing_Logic": "Keys and facts only for analytical performance", 
                "Field_Limit": "Keys + Facts", 
                "Use_Cases": "Power BI model optimization"
            }
        ]
        return relations
