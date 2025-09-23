"""
Relation Processor
==================

Handles deterministic relation processing logic for column cascading.
Provides context-aware cascading based on artifact types, stages, and relation types.
"""

# ANCHOR: Imports and Dependencies
from enum import Enum
from typing import List, Dict, Any, Optional
import pandas as pd
from pathlib import Path
import sys

# Import utilities
current_dir = Path(__file__).parent
src_dir = current_dir.parent
sys.path.insert(0, str(src_dir))

from utils.c_workbench_config_utils import ConfigManager
from utils.z_logger import Logger

# ANCHOR: Enums and Constants
class ArtifactType(Enum):
    """Supported artifact types for context-aware processing."""
    DIMENSION = "dimension"
    FACT = "fact"
    BRIDGE = "bridge"
    UNKNOWN = "unknown"

class StageTransition(Enum):
    """Common stage transition patterns."""
    DROP_TO_BRONZE = "s0_to_s1"      # 0_drop_zone → 1_bronze
    BRONZE_TO_SILVER = "s1_to_s2"    # 1_bronze → 2_silver
    SILVER_TO_GOLD = "s2_to_s3"      # 2_silver → 3_gold
    GOLD_TO_MART = "s3_to_s4"        # 3_gold → 4_mart
    MART_TO_PBI = "s4_to_s5"         # 4_mart → 5_PBI_Model
    PBI_MODEL_TO_REPORT = "s5_to_s6" # 5_PBI_Model → 6_PBI_Reports

# ANCHOR: RelationProcessor Class
class RelationProcessor:
    """
    Deterministic relation processing engine for enhanced column cascading.
    """
    
    def __init__(self):
        self.config = ConfigManager()
        self.logger = Logger()
        
    # ANCHOR: Artifact Type Detection
    def detect_artifact_type(self, artifact_name: str, artifact_type_field: str = None) -> ArtifactType:
        """
        Detect artifact type from name patterns and explicit type field.
        
        Args:
            artifact_name: Name of the artifact
            artifact_type_field: Explicit artifact type from Artifacts sheet
            
        Returns:
            ArtifactType: Detected artifact type
        """
        # Check explicit type field first
        if artifact_type_field:
            artifact_type_lower = artifact_type_field.lower()
            if artifact_type_lower == "dimension":
                return ArtifactType.DIMENSION
            elif artifact_type_lower == "fact":
                return ArtifactType.FACT
            elif artifact_type_lower == "bridge":
                return ArtifactType.BRIDGE
        
        # Pattern-based detection
        name_lower = artifact_name.lower()
            
        # Dimension patterns: dim_, dimension_, d_
        if any(name_lower.startswith(prefix) for prefix in ["dim_", "dimension_", "d_"]):
            return ArtifactType.DIMENSION
            
        # Fact patterns: fact_, f_, contains "fact"
        if any(pattern in name_lower for pattern in ["fact_", "f_", "fact"]):
            return ArtifactType.FACT
            
        # Bridge patterns: bridge_, br_, contains "bridge"
        if any(pattern in name_lower for pattern in ["bridge_", "br_", "bridge"]):
            return ArtifactType.BRIDGE
        
        self.logger.warning(f"Could not detect artifact type for: {artifact_name}")
        return ArtifactType.UNKNOWN
    
    def detect_stage_transition(self, source_stage: str, target_stage: str) -> Optional[StageTransition]:
        """
        Detect the type of stage transition for context-aware processing.
        
        Args:
            source_stage: Source stage ID (e.g., "s1")
            target_stage: Target stage ID (e.g., "s2")
            
        Returns:
            StageTransition: Detected transition type or None
        """
        transition_map = {
            ("s0", "s1"): StageTransition.DROP_TO_BRONZE,
            ("s1", "s2"): StageTransition.BRONZE_TO_SILVER,
            ("s2", "s3"): StageTransition.SILVER_TO_GOLD,
            ("s3", "s4"): StageTransition.GOLD_TO_MART,
            ("s4", "s5"): StageTransition.MART_TO_PBI,
            ("s5", "s6"): StageTransition.PBI_MODEL_TO_REPORT,
        }
        
        return transition_map.get((source_stage, target_stage))
    
    # ANCHOR: Enhanced Relation Methods
    def process_main_relation(self, 
                            source_columns: List[Dict], 
                            source_stage: str,
                            target_stage: str,
                            target_artifact_type: ArtifactType) -> List[Dict]:
        """
        Enhanced main relation processing with context awareness.
        
        Args:
            source_columns: List of source column dictionaries
            source_stage: Source stage ID
            target_stage: Target stage ID  
            target_artifact_type: Type of target artifact
            
        Returns:
            List[Dict]: Processed columns for target artifact
        """
        self.logger.info(f"Processing main relation: {source_stage} → {target_stage}, type: {target_artifact_type.value}")
        
        # Start with source columns
        processed_columns = source_columns.copy()
        
        # Get stage transition context
        transition = self.detect_stage_transition(source_stage, target_stage)
        
        # Apply stage-specific transformations
        if transition:
            processed_columns = self._apply_stage_transformations(processed_columns, transition)
        
        # Apply artifact-type specific logic
        processed_columns = self._apply_artifact_type_logic(processed_columns, target_artifact_type)
        
        # Add technical fields based on stage and artifact type
        technical_fields = self._get_technical_fields(target_stage, target_artifact_type)
        processed_columns.extend(technical_fields)
        
        return processed_columns
    
    def process_get_key_relation(self, 
                               source_columns: List[Dict], 
                               target_artifact_type: ArtifactType) -> List[Dict]:
        """
        Enhanced get_key relation for dimension key propagation to fact tables.
        
        Args:
            source_columns: Source dimension columns
            target_artifact_type: Should be FACT for this relation type
            
        Returns:
            List[Dict]: Key columns for fact table
        """
        self.logger.info(f"Processing get_key relation for {target_artifact_type.value}")
        
        key_columns = []
        
        # Extract surrogate keys (SKs) and business keys (BKs)
        for col in source_columns:
            col_name = col.get('column_name', '').lower()
            col_group = col.get('column_group', '').lower()
            
            # Include surrogate keys
            if col_group == 'sks' or col_name.endswith('_sk'):
                key_columns.append(col.copy())
            
            # Include business keys for reference
            elif col_group == 'bks' or col_name.endswith('_bk'):
                key_columns.append(col.copy())
        
        return key_columns
    
    def process_lookup_relation(self, 
                              source_columns: List[Dict], 
                              field_limit: int = 3) -> List[Dict]:
        """
        Enhanced lookup relation with configurable field limits.
        
        Args:
            source_columns: Source columns
            field_limit: Maximum number of fields to include
            
        Returns:
            List[Dict]: Limited set of lookup columns
        """
        self.logger.info(f"Processing lookup relation with limit: {field_limit}")
        
        # Priority order for lookup fields
        priority_groups = ['sks', 'bks', 'attributes']
        lookup_columns = []
        
        for group in priority_groups:
            if len(lookup_columns) >= field_limit:
                break
                
            for col in source_columns:
                if len(lookup_columns) >= field_limit:
                    break
                    
                col_group = col.get('column_group', '').lower()
                if col_group == group:
                    lookup_columns.append(col.copy())
        
        return lookup_columns[:field_limit]
    
    def process_pbi_relation(self, source_columns: List[Dict]) -> List[Dict]:
        """
        Power BI specific relation processing (minimal impact).
        
        Args:
            source_columns: Source columns
            
        Returns:
            List[Dict]: Columns optimized for Power BI
        """
        self.logger.info("Processing Power BI relation (minimal cascading)")
        
        # For PBI, typically we just pass through key fields and measures
        pbi_columns = []
        
        for col in source_columns:
            col_group = col.get('column_group', '').lower()
            
            # Include keys and facts for Power BI models
            if col_group in ['sks', 'bks', 'facts']:
                pbi_columns.append(col.copy())
        
        return pbi_columns
    
    # ANCHOR: Helper Methods
    def _apply_stage_transformations(self, columns: List[Dict], transition: StageTransition) -> List[Dict]:
        """Apply stage-specific column transformations."""
        
        if transition == StageTransition.BRONZE_TO_SILVER:
            # Bronze → Silver: Clean naming, standardize types
            for col in columns:
                # Remove bronze prefixes, standardize naming
                col_name = col.get('column_name', '')
                if col_name.startswith('bronze_'):
                    col['column_name'] = col_name.replace('bronze_', '')
        
        elif transition == StageTransition.SILVER_TO_GOLD:
            # Silver → Gold: Prepare for analytical use
            for col in columns:
                # Optimize data types for analytics
                data_type = col.get('data_type', '')
                if data_type == 'varchar':
                    # Consider converting to more specific types in gold
                    pass
        
        return columns
    
    def _apply_artifact_type_logic(self, columns: List[Dict], artifact_type: ArtifactType) -> List[Dict]:
        """Apply artifact-type specific column logic."""
        
        if artifact_type == ArtifactType.FACT:
            # Facts: Ensure measures are properly typed
            for col in columns:
                col_group = col.get('column_group', '').lower()
                if col_group == 'facts':
                    # Ensure numeric types for measures
                    data_type = col.get('data_type', '')
                    if data_type in ['varchar', 'text']:
                        col['data_type'] = 'decimal(18,2)'  # Default measure type
        
        return columns
    
    def _get_technical_fields(self, stage: str, artifact_type: ArtifactType) -> List[Dict]:
        """Get stage and artifact-type specific technical fields."""
        
        technical_fields = []
        base_order = 1000  # Technical fields go at end
        
        # Common technical fields for all stages
        common_fields = [
            {'column_name': f'__{stage}_loadDate', 'data_type': 'datetime2', 'column_group': 'technical_fields'},
            {'column_name': f'__{stage}_source', 'data_type': 'varchar(100)', 'column_group': 'technical_fields'},
        ]
        
        # Stage-specific technical fields
        if stage == 's2':  # Silver
            common_fields.extend([
                {'column_name': '__silver_validFrom', 'data_type': 'datetime2', 'column_group': 'technical_fields'},
                {'column_name': '__silver_validTo', 'data_type': 'datetime2', 'column_group': 'technical_fields'},
            ])
        
        elif stage == 's3':  # Gold
            common_fields.extend([
                {'column_name': '__gold_lastRefresh', 'data_type': 'datetime2', 'column_group': 'technical_fields'},
                {'column_name': '__gold_aggregationLevel', 'data_type': 'varchar(50)', 'column_group': 'technical_fields'},
            ])
        
        # Artifact-type specific technical fields
        if artifact_type == ArtifactType.DIMENSION:
            common_fields.extend([
                {'column_name': '__dim_scdType', 'data_type': 'int', 'column_group': 'technical_fields'},
                {'column_name': '__dim_isCurrent', 'data_type': 'bit', 'column_group': 'technical_fields'},
            ])
        
        elif artifact_type == ArtifactType.FACT:
            common_fields.extend([
                {'column_name': '__fact_grainLevel', 'data_type': 'varchar(100)', 'column_group': 'technical_fields'},
                {'column_name': '__fact_measureUnit', 'data_type': 'varchar(50)', 'column_group': 'technical_fields'},
            ])
        
        # Add order numbers to technical fields
        for i, field in enumerate(common_fields):
            field['order'] = base_order + i
        
        return common_fields