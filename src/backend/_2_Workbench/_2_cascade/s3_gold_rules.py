"""
Stage s3 - Gold Cascade Rules
===============================
Rules from CASCADE_and_OTHER_RULES.xlsx - Cascading_Rules sheet
"""

import pandas as pd
from typing import Dict, List, Optional


class S3GoldRules:
    """Implements cascade rules for s3 (3_gold) stage."""
    
    def __init__(self):
        self.stage_id = "s3"
        self.stage_name = "3_gold"
    
    def rule_gld_1_field_selection(
        self,
        upstream_columns_df: pd.DataFrame,
        target_columns_df: pd.DataFrame,
        artifact_id: str,
        upstream_relation: str
    ) -> pd.DataFrame:
        """
        Rule gld-1: Field Selection
        
        Description: Take ALL fields from upstream (s2) (only from main upstream relation))
                     EXCEPT technical & partition fields
        Applies to: All artifacts
        Notes: First business-side stage - Group names: attributes or facts
        """
        # Only process main upstream relation
        if upstream_relation.lower() != 'main':
            return pd.DataFrame()
        
        # Filter out technical and partition fields from upstream
        non_tech_columns = upstream_columns_df[
            ~upstream_columns_df['column_group'].str.contains('technical|partition', case=False, na=False, regex=True)
        ].copy()
        
        # Get existing column names in target artifact
        existing_columns = target_columns_df[
            target_columns_df['artifact_id'] == artifact_id
        ]['column_name'].tolist()
        
        # Filter out duplicates
        new_columns = non_tech_columns[
            ~non_tech_columns['column_name'].isin(existing_columns)
        ].copy()
        
        return new_columns
    
    def rule_gld_2_dimension_sk(
        self,
        columns_df: pd.DataFrame,
        artifact_id: str,
        artifact_name: str,
        artifact_type: str
    ) -> pd.DataFrame:
        """
        Rule gld-2: dimension SK surrogate key
        
        Description: Add in the beginning: {artifact_name}_SK bigint surrogate key
        Applies to: dimensions
        Notes: group name: surrogate key
        """
        if artifact_type.lower() != 'dimension':
            return columns_df
        
        # Create SK field
        sk_field = {
            'artifact_id': artifact_id,
            'artifact_name': artifact_name,
            'stage_id': self.stage_id,
            'stage_name': self.stage_name,
            'column_name': f'{artifact_name}_SK',
            'data_type': 'BIGINT',
            'order': 1,
            'column_group': 'surrogate key',
            'column_business_name': f'{artifact_name}_surrogate_key',
            'column_comment': f'Surrogate key for {artifact_name}',
            'source_column_name': f'{artifact_name}_SK',
            'lookup_fields': '',
            'etl_simple_trnasformation': '',
            'ai_transformation_prompt': '',
            'etl_ai_transformation': ''
        }
        
        # Adjust order of existing columns
        columns_df['order'] = columns_df['order'] + 1
        
        # Prepend SK field
        sk_df = pd.DataFrame([sk_field])
        columns_df = pd.concat([sk_df, columns_df], ignore_index=True)
        
        return columns_df
    
    def rule_gld_3_facts_sks(
        self,
        columns_df: pd.DataFrame,
        artifact_id: str,
        artifact_name: str,
        artifact_type: str,
        upstream_artifacts_df: pd.DataFrame,
        get_key_relations: List[str]
    ) -> pd.DataFrame:
        """
        Rule gld-3: Facts SKs
        
        Description: Add in the beginning: {upstream artifact_name}_SK bigint surrogate key
                     for each upstream artifact with "get_key" upstream relation
        Applies to: facts
        Notes: group name: surrogate keys
        """
        if artifact_type.lower() != 'fact':
            return columns_df
        
        # Create SK fields for each get_key upstream artifact
        sk_fields = []
        for order, upstream_artifact_id in enumerate(get_key_relations, start=1):
            # Get upstream artifact name
            upstream_match = upstream_artifacts_df[
                upstream_artifacts_df['artifact_id'] == upstream_artifact_id
            ]
            
            if not upstream_match.empty:
                upstream_name = upstream_match.iloc[0]['artifact_name']
                
                sk_field = {
                    'artifact_id': artifact_id,
                    'artifact_name': artifact_name,
                    'stage_id': self.stage_id,
                    'stage_name': self.stage_name,
                    'column_name': f'{upstream_name}_SK',
                    'data_type': 'BIGINT',
                    'order': order,
                    'column_group': 'surrogate keys',
                    'column_business_name': f'{upstream_name}_surrogate_key',
                    'column_comment': f'Surrogate key from {upstream_name}',
                    'source_column_name': f'{upstream_name}_SK',
                    'lookup_fields': '',
                    'etl_simple_trnasformation': '',
                    'ai_transformation_prompt': '',
                    'etl_ai_transformation': ''
                }
                sk_fields.append(sk_field)
        
        if sk_fields:
            # Adjust order of existing columns
            columns_df['order'] = columns_df['order'] + len(sk_fields)
            
            # Prepend SK fields
            sk_df = pd.DataFrame(sk_fields)
            columns_df = pd.concat([sk_df, columns_df], ignore_index=True)
        
        return columns_df
    
    def rule_gld_4_dimension_bk(
        self,
        columns_df: pd.DataFrame,
        artifact_id: str,
        artifact_name: str,
        artifact_type: str
    ) -> pd.DataFrame:
        """
        Rule gld-4: dimension BK business key
        
        Description: following the SK we have the {artifact_name}_BK datatype business key
        Applies to: dimensions
        Notes: Group name: business key - Datatype manually injected (empty when cascading).
               Color data type cell as red. the etl_simple_transformation dictates the data type of the BK
        """
        if artifact_type.lower() != 'dimension':
            return columns_df
        
        # Create BK field (after SK at order 2)
        bk_field = {
            'artifact_id': artifact_id,
            'artifact_name': artifact_name,
            'stage_id': self.stage_id,
            'stage_name': self.stage_name,
            'column_name': f'{artifact_name}_BK',
            'data_type': '',  # Empty - manually injected, dictated by etl_simple_transformation
            'order': 2,
            'column_group': 'business key',
            'column_business_name': f'{artifact_name}_business_key',
            'column_comment': f'Business key for {artifact_name}',
            'source_column_name': f'{artifact_name}_BK',
            'lookup_fields': '',
            'etl_simple_trnasformation': '',  # This dictates the BK data type
            'ai_transformation_prompt': '',
            'etl_ai_transformation': ''
        }
        
        # Find position after SK (order 1)
        sk_idx = columns_df[columns_df['order'] == 1].index
        if not sk_idx.empty:
            # Insert BK after SK
            columns_df.loc[columns_df['order'] > 1, 'order'] += 1
            bk_df = pd.DataFrame([bk_field])
            columns_df = pd.concat([columns_df, bk_df], ignore_index=True)
            columns_df = columns_df.sort_values('order').reset_index(drop=True)
        
        return columns_df
    
    def rule_gld_5_facts_bks(
        self,
        columns_df: pd.DataFrame,
        artifact_id: str,
        artifact_name: str,
        artifact_type: str,
        upstream_artifacts_df: pd.DataFrame,
        get_key_relations: List[str]
    ) -> pd.DataFrame:
        """
        Rule gld-5: Facts BKs business keys
        
        Description: following the SKs we have the {upstream artifact_name}_BK datatype business key
                     for each upstream artifact with "get_key" upstream relation
        Applies to: facts
        Notes: Group name: business key
        """
        if artifact_type.lower() != 'fact':
            return columns_df
        
        # Count existing SKs
        sk_count = len(get_key_relations)
        
        # Create BK fields for each get_key upstream artifact
        bk_fields = []
        for order_offset, upstream_artifact_id in enumerate(get_key_relations, start=1):
            # Get upstream artifact name
            upstream_match = upstream_artifacts_df[
                upstream_artifacts_df['artifact_id'] == upstream_artifact_id
            ]
            
            if not upstream_match.empty:
                upstream_name = upstream_match.iloc[0]['artifact_name']
                
                bk_field = {
                    'artifact_id': artifact_id,
                    'artifact_name': artifact_name,
                    'stage_id': self.stage_id,
                    'stage_name': self.stage_name,
                    'column_name': f'{upstream_name}_BK',
                    'data_type': '',  # Empty - dictated by etl_simple_transformation
                    'order': sk_count + order_offset,
                    'column_group': 'business key',
                    'column_business_name': f'{upstream_name}_business_key',
                    'column_comment': f'Business key from {upstream_name}',
                    'source_column_name': f'{upstream_name}_BK',
                    'lookup_fields': '',
                    'etl_simple_trnasformation': '',  # This dictates the BK data type
                    'ai_transformation_prompt': '',
                    'etl_ai_transformation': ''
                }
                bk_fields.append(bk_field)
        
        if bk_fields:
            # Adjust order of existing columns after SKs
            columns_df.loc[columns_df['order'] > sk_count, 'order'] += len(bk_fields)
            
            # Insert BK fields
            bk_df = pd.DataFrame(bk_fields)
            columns_df = pd.concat([columns_df, bk_df], ignore_index=True)
            columns_df = columns_df.sort_values('order').reset_index(drop=True)
        
        return columns_df
    
    def rule_gld_6_technical_fields(
        self,
        columns_df: pd.DataFrame,
        artifact_id: str,
        artifact_name: str
    ) -> pd.DataFrame:
        """
        Rule gld-6: Technical fields
        
        Description: add at the end of the fields list the following fields /datatypes/column_group:
                     __{s3}_last_update_dt  TIMESTAMP  technical field
        Applies to: All artifacts
        Notes: partition technical fields are optional and manual injected
        """
        # Get the max order
        max_order = columns_df['order'].max() if len(columns_df) > 0 else 0
        
        # Define technical fields for s3/gold
        technical_fields = [
            {
                'artifact_id': artifact_id,
                'artifact_name': artifact_name,
                'stage_id': self.stage_id,
                'stage_name': self.stage_name,
                'column_name': f'__{self.stage_name}_last_update_dt',
                'data_type': 'TIMESTAMP',
                'column_group': 'technical field',
                'order': max_order + 1,
                'column_business_name': f'{self.stage_name}_last_update_date',
                'column_comment': f'Last update timestamp for {self.stage_name} stage',
                'source_column_name': f'__{self.stage_name}_last_update_dt',
                'lookup_fields': '',
                'etl_simple_trnasformation': '',
                'ai_transformation_prompt': '',
                'etl_ai_transformation': ''
            }
        ]
        
        # Append technical fields
        tech_df = pd.DataFrame(technical_fields)
        columns_df = pd.concat([columns_df, tech_df], ignore_index=True)
        
        return columns_df
    
    def rule_gld_7_naming(
        self,
        columns_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Rule gld-7: Naming
        
        Description: Use column_business_name if available, else source name
        Applies to: All artifacts
        Notes: Business-friendly naming starts here
        """
        for idx, row in columns_df.iterrows():
            business_name = row.get('column_business_name', '')
            source_name = row.get('column_name', '')
            
            # Use business name if available, otherwise keep source name
            if pd.notna(business_name) and business_name != '':
                columns_df.at[idx, 'column_name'] = business_name
        
        return columns_df
    
    def rule_gld_8_data_types(
        self,
        columns_df: pd.DataFrame,
        s2_columns_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Rule gld-8: Data Types
        
        Description: use data types of s2
        Applies to: All artifacts
        """
        # Map data types from s2 to current columns
        for idx, row in columns_df.iterrows():
            source_column_name = row.get('source_column_name', '')
            
            # Find matching column in s2
            s2_match = s2_columns_df[
                s2_columns_df['column_name'] == source_column_name
            ]
            
            if not s2_match.empty:
                s2_row = s2_match.iloc[0]
                # Only set if current data_type is empty (preserve manually set types like SK/BK)
                if pd.isna(row.get('data_type', '')) or row.get('data_type', '') == '':
                    columns_df.at[idx, 'data_type'] = s2_row['data_type']
        
        return columns_df
    
    def rule_gld_9_source_columns(
        self,
        columns_df: pd.DataFrame,
        s2_columns_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Rule gld-9: source columns
        
        Description: source_column_name coming from s2
        Applies to: All artifacts
        """
        # source_column_name should already be set from s2
        # This rule confirms that behavior
        for idx, row in columns_df.iterrows():
            if pd.isna(row.get('source_column_name', '')) or row.get('source_column_name', '') == '':
                # If not set, use column_name
                columns_df.at[idx, 'source_column_name'] = row['column_name']
        
        return columns_df
