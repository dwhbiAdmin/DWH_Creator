"""
Stage s2 - Silver Cascade Rules
=================================
Rules from CASCADE_and_OTHER_RULES.xlsx - Cascading_Rules sheet
"""

import pandas as pd
from typing import Dict, List, Optional


class S2SilverRules:
    """Implements cascade rules for s2 (2_silver) stage."""
    
    def __init__(self):
        self.stage_id = "s2"
        self.stage_name = "2_silver"
    
    def rule_slv_1_field_selection(
        self,
        upstream_columns_df: pd.DataFrame,
        target_columns_df: pd.DataFrame,
        artifact_id: str
    ) -> pd.DataFrame:
        """
        Rule slv-1: Field Selection
        
        Description: Take ALL fields from upstream (s1) EXCEPT partition fields
        Applies to: All artifacts
        Notes: Duplicate prevention active
        """
        # Filter out partition fields from upstream
        non_partition_columns = upstream_columns_df[
            ~upstream_columns_df['column_group'].str.contains('partition', case=False, na=False)
        ].copy()
        
        # Get existing column names in target artifact
        existing_columns = target_columns_df[
            target_columns_df['artifact_id'] == artifact_id
        ]['column_name'].tolist()
        
        # Filter out duplicates
        new_columns = non_partition_columns[
            ~non_partition_columns['column_name'].isin(existing_columns)
        ].copy()
        
        return new_columns
    
    def rule_slv_2_table_primary_keys(
        self,
        columns_df: pd.DataFrame,
        s0_columns_df: pd.DataFrame,
        artifact_id: str,
        artifact_name: str
    ) -> pd.DataFrame:
        """
        Rule slv-2: Table Primary keys
        
        Description: Add in the beginning: {column_name}_PK for each column 
                     identified as PK-primary key in the s0 stage (rule 2)
        Applies to: All artifacts
        Notes: a table can have more than one primary keys
        """
        # Find primary keys from s0
        pk_columns = s0_columns_df[
            s0_columns_df['column_group'].str.contains('primary key', case=False, na=False)
        ]
        
        # Create PK fields
        pk_fields = []
        for order, (idx, pk_row) in enumerate(pk_columns.iterrows(), start=1):
            pk_field = {
                'artifact_id': artifact_id,
                'artifact_name': artifact_name,
                'stage_id': self.stage_id,
                'stage_name': self.stage_name,
                'column_name': f"{pk_row['column_name']}_PK",
                'data_type': pk_row['data_type'],
                'order': order,
                'column_group': 'primary key',
                'column_business_name': f"{pk_row.get('column_business_name', pk_row['column_name'])}_PK",
                'column_comment': f"Primary key from {pk_row['column_name']}",
                'source_column_name': pk_row['column_name'],
                'lookup_fields': '',
                'etl_simple_trnasformation': '',
                'ai_transformation_prompt': '',
                'etl_ai_transformation': ''
            }
            pk_fields.append(pk_field)
        
        # Prepend PK fields to the beginning
        if pk_fields:
            pk_df = pd.DataFrame(pk_fields)
            
            # Adjust order of existing columns
            columns_df['order'] = columns_df['order'] + len(pk_fields)
            
            # Combine
            columns_df = pd.concat([pk_df, columns_df], ignore_index=True)
        
        return columns_df
    
    def rule_slv_3_technical_fields(
        self,
        columns_df: pd.DataFrame,
        artifact_id: str,
        artifact_name: str
    ) -> pd.DataFrame:
        """
        Rule slv-3: Technical fields
        
        Description: add at the end of the fields list the following fields /datatypes/column_group:
                     __SourceSystem        STRING      technical field
                     __SourceFileName      STRING      technical field
                     __SourceFilePath      STRING      technical field
                     __{s1}_insert_dt      TIMESTAMP   technical field
                     __{s2}_last_update_dt TIMESTAMP   technical field
        Applies to: All artifacts
        Notes: technical fields & optional partitions manual injected for very large tables
        """
        # Get the max order
        max_order = columns_df['order'].max() if len(columns_df) > 0 else 0
        
        # Define technical fields for s2/silver
        technical_fields = [
            {
                'column_name': '__SourceSystem',
                'data_type': 'STRING',
                'column_group': 'technical field',
                'order': max_order + 1
            },
            {
                'column_name': '__SourceFileName',
                'data_type': 'STRING',
                'column_group': 'technical field',
                'order': max_order + 2
            },
            {
                'column_name': '__SourceFilePath',
                'data_type': 'STRING',
                'column_group': 'technical field',
                'order': max_order + 3
            },
            {
                'column_name': '__1_bronze_insert_dt',
                'data_type': 'TIMESTAMP',
                'column_group': 'technical field',
                'order': max_order + 4
            },
            {
                'column_name': f'__{self.stage_name}_last_update_dt',
                'data_type': 'TIMESTAMP',
                'column_group': 'technical field',
                'order': max_order + 5
            }
        ]
        
        # Add artifact info to technical fields
        for field in technical_fields:
            field['artifact_id'] = artifact_id
            field['artifact_name'] = artifact_name
            field['stage_id'] = self.stage_id
            field['stage_name'] = self.stage_name
        
        # Append technical fields
        tech_df = pd.DataFrame(technical_fields)
        columns_df = pd.concat([columns_df, tech_df], ignore_index=True)
        
        return columns_df
    
    def rule_slv_4_naming(
        self,
        columns_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Rule slv-4: Naming
        
        Description: Use source column names
        Applies to: All artifacts
        Notes: Still on source side
        """
        # Column names are preserved from upstream
        # No transformation needed
        return columns_df
    
    def rule_slv_5_data_types(
        self,
        columns_df: pd.DataFrame,
        s0_columns_df: pd.DataFrame,
        data_mappings_df: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        """
        Rule slv-5: Data Types
        
        Description: Keep source data types from s0 not s1. Convert to target platform (if different)
        Applies to: All artifacts
        Notes: we have a "casting module" - Use conf_4_data_mappings for conversions
        """
        # Map data types from s0 to current columns
        for idx, row in columns_df.iterrows():
            column_name = row['column_name']
            
            # Find matching column in s0
            s0_match = s0_columns_df[
                s0_columns_df['column_name'] == column_name
            ]
            
            if not s0_match.empty:
                s0_row = s0_match.iloc[0]
                source_data_type = s0_row['data_type']
                
                # TODO: Apply data_mappings_df conversion if platform changes
                # For now, keep s0 data type
                columns_df.at[idx, 'data_type'] = source_data_type
        
        return columns_df
    
    def rule_slv_6_source_columns(
        self,
        columns_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Rule slv-6: source columns
        
        Description: source_column_name is equal to column_name
        Applies to: All artifacts
        Notes: Still on source side
        """
        columns_df['source_column_name'] = columns_df['column_name']
        return columns_df
    
    def rule_slv_7_other_fields(
        self,
        columns_df: pd.DataFrame,
        s0_columns_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Rule slv-7: other fields
        
        Description: source_column_name = column name except for PK
                     lookup_fields: empty
                     etl_simple_trnasformation: empty
                     ai_transformation_prompt: empty
                     etl_ai_transformation: empty
                     column_business_name: copy from s0
                     column_group: "source fields" except for Primary keys
                     column_comment: copy from s0
        Applies to: All artifacts
        """
        # Set empty values for transformation fields
        columns_df['lookup_fields'] = ''
        columns_df['etl_simple_trnasformation'] = ''
        columns_df['ai_transformation_prompt'] = ''
        columns_df['etl_ai_transformation'] = ''
        
        # Process each column
        for idx, row in columns_df.iterrows():
            column_name = row['column_name']
            column_group = str(row.get('column_group', ''))
            
            # Set source_column_name (except for PK fields which have _PK suffix)
            if '_PK' in column_name:
                # For PK fields, source is the original column name without _PK
                columns_df.at[idx, 'source_column_name'] = column_name.replace('_PK', '')
            else:
                columns_df.at[idx, 'source_column_name'] = column_name
            
            # Find matching column in s0
            base_column_name = column_name.replace('_PK', '') if '_PK' in column_name else column_name
            s0_match = s0_columns_df[
                s0_columns_df['column_name'] == base_column_name
            ]
            
            if not s0_match.empty:
                s0_row = s0_match.iloc[0]
                columns_df.at[idx, 'column_business_name'] = s0_row.get('column_business_name', '')
                columns_df.at[idx, 'column_comment'] = s0_row.get('column_comment', '')
            
            # Set column_group to "source fields" except for primary keys and technical fields
            if 'primary key' not in column_group.lower() and 'technical' not in column_group.lower() and 'partition' not in column_group.lower():
                columns_df.at[idx, 'column_group'] = 'source fields'
        
        return columns_df
