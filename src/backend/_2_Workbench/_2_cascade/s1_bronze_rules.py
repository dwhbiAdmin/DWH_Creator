"""
Stage s1 - Bronze Cascade Rules
=================================
Rules from CASCADE_and_OTHER_RULES.xlsx - Cascading_Rules sheet
"""

import pandas as pd
from typing import Dict, List, Optional


class S1BronzeRules:
    """Implements cascade rules for s1 (1_bronze) stage."""
    
    def __init__(self):
        self.stage_id = "s1"
        self.stage_name = "1_bronze"
    
    def rule_brz_1_field_selection(
        self,
        upstream_columns_df: pd.DataFrame,
        target_columns_df: pd.DataFrame,
        artifact_id: str
    ) -> pd.DataFrame:
        """
        Rule brz-1: Field Selection
        
        Description: Take ALL fields from upstream (s0)
        Applies to: All artifacts
        Notes: Skip columns that already exist in target
        """
        # Get existing column names in target artifact
        existing_columns = target_columns_df[
            target_columns_df['artifact_id'] == artifact_id
        ]['column_name'].tolist()
        
        # Filter out columns that already exist
        new_columns = upstream_columns_df[
            ~upstream_columns_df['column_name'].isin(existing_columns)
        ].copy()
        
        return new_columns
    
    def rule_brz_2_naming(
        self,
        columns_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Rule brz-2: Naming
        
        Description: Use source column names as-is
        Applies to: All artifacts
        Notes: Source side: preserve technical names
        """
        # Column names are already preserved from upstream
        # No transformation needed - column_name stays as-is
        return columns_df
    
    def rule_brz_3_source_columns(
        self,
        columns_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Rule brz-3: source columns
        
        Description: source_column_name is equal to column_name
        Applies to: All artifacts
        Notes: Source side: preserve technical names
        """
        columns_df['source_column_name'] = columns_df['column_name']
        return columns_df
    
    def rule_brz_4_data_types(
        self,
        columns_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Rule brz-4: Data Types
        
        Description: all of type STRING
        Applies to: All artifacts
        Notes: except for technical fields & partition fields
        """
        # Set all columns to STRING except technical and partition fields
        for idx, row in columns_df.iterrows():
            column_group = str(row.get('column_group', '')).lower()
            
            # Skip technical and partition fields
            if 'technical' not in column_group and 'partition' not in column_group:
                columns_df.at[idx, 'data_type'] = 'STRING'
        
        return columns_df
    
    def rule_brz_5_order(
        self,
        columns_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Rule brz-5: Order
        
        Description: Preserve source order; start from 1
        Applies to: All artifacts
        Notes: comment copied from upstream
        """
        # Renumber order starting from 1
        columns_df['order'] = range(1, len(columns_df) + 1)
        
        # Column comment is already copied from upstream
        return columns_df
    
    def rule_brz_6_business_names_ai(
        self,
        columns_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Rule brz-6: Business names (AI)
        
        Description: column_business_name is AI estimation
        Applies to: All artifacts
        Notes: skip if already estimated
        """
        # TODO: Implement AI estimation for column_business_name
        # Skip if already estimated
        return columns_df
    
    def rule_brz_7_technical_fields(
        self,
        columns_df: pd.DataFrame,
        artifact_id: str,
        artifact_name: str
    ) -> pd.DataFrame:
        """
        Rule brz-7: Technical fields
        
        Description: add at the end of the fields list the following fields /datatypes/column_group:
                     __SourceSystem        STRING      technical field
                     __SourceFileName      STRING      technical field
                     __SourceFilePath      STRING      technical field
                     __{s1}_insert_dt      TIMESTAMP   technical field
                     __{s1}_Partition_InsertYear   int   partition field
                     __{s1}_Partition_InsertMonth  int   partition field
                     __{s1}_Partition_insertDate   int   partition field
        Applies to: All artifacts
        Notes: the __{s1}_insert_dt is the CDC field (change data capture)
        """
        # Get the max order
        max_order = columns_df['order'].max() if len(columns_df) > 0 else 0
        
        # Define technical fields for s1/bronze
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
                'column_name': f'__{self.stage_name}_insert_dt',
                'data_type': 'TIMESTAMP',
                'column_group': 'technical field',
                'order': max_order + 4
            },
            {
                'column_name': f'__{self.stage_name}_Partition_InsertYear',
                'data_type': 'INT',
                'column_group': 'partition field',
                'order': max_order + 5
            },
            {
                'column_name': f'__{self.stage_name}_Partition_InsertMonth',
                'data_type': 'INT',
                'column_group': 'partition field',
                'order': max_order + 6
            },
            {
                'column_name': f'__{self.stage_name}_Partition_insertDate',
                'data_type': 'INT',
                'column_group': 'partition field',
                'order': max_order + 7
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
    
    def rule_brz_8_other_fields(
        self,
        columns_df: pd.DataFrame,
        upstream_columns_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Rule brz-8: other fields
        
        Description: source_column_name = column_name
                     lookup_fields: empty
                     etl_simple_trnasformation: empty
                     ai_transformation_prompt: empty
                     etl_ai_transformation: empty
                     column_business_name: copy from s0
                     column_group: "source fields"
                     column_comment: copy from s0
        Applies to: All artifacts
        """
        # Set source_column_name to column_name
        columns_df['source_column_name'] = columns_df['column_name']
        
        # Set empty values for transformation fields
        columns_df['lookup_fields'] = ''
        columns_df['etl_simple_trnasformation'] = ''
        columns_df['ai_transformation_prompt'] = ''
        columns_df['etl_ai_transformation'] = ''
        
        # Copy column_business_name and column_comment from s0 (upstream)
        for idx, row in columns_df.iterrows():
            column_name = row['column_name']
            
            # Find matching column in upstream
            upstream_match = upstream_columns_df[
                upstream_columns_df['column_name'] == column_name
            ]
            
            if not upstream_match.empty:
                upstream_row = upstream_match.iloc[0]
                columns_df.at[idx, 'column_business_name'] = upstream_row.get('column_business_name', '')
                columns_df.at[idx, 'column_comment'] = upstream_row.get('column_comment', '')
        
        # Set column_group to "source fields" for non-technical columns
        for idx, row in columns_df.iterrows():
            column_group = str(row.get('column_group', ''))
            if 'technical' not in column_group.lower() and 'partition' not in column_group.lower():
                columns_df.at[idx, 'column_group'] = 'source fields'
        
        return columns_df
