"""
Stage s0 - Drop Zone Cascade Rules
====================================
Rules from CASCADE_and_OTHER_RULES.xlsx - Cascading_Rules sheet
"""

import pandas as pd
from typing import Dict, List


class S0DropZoneRules:
    """Implements cascade rules for s0 (0_drop_zone) stage."""
    
    def __init__(self):
        self.stage_id = "s0"
        self.stage_name = "0_drop_zone"
    
    def rule_drp_1_ai_estimate_data_types_and_business_names(
        self, 
        columns_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Rule drp-1: Data Types & business names & Column Comment (AI)
        
        Description: columns : data_type and column_business_name and 
                     column_comment are AI estimated
        Applies to: All artifacts
        Notes: skip if already estimated
        """
        # TODO: Implement AI estimation for data_type, column_business_name, 
        # column_comment
        # Skip if already estimated
        return columns_df
    
    def rule_drp_2_ai_estimate_primary_keys(
        self, 
        columns_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Rule drp-2: primary key (AI)
        
        Description: use AI to estimate primary keys and fill in the column_group.
        Applies to: All artifacts
        Notes: Indication of primary key are words like containing : ID, PK etc.
               All other columns have column_group="source column"
        """
        # Check for primary key indicators in column names
        pk_indicators = ['id', 'pk', 'key', '_id', 'code']
        
        for idx, row in columns_df.iterrows():
            column_name = str(row['column_name']).lower()
            
            # Check if column name contains primary key indicators
            is_likely_pk = any(indicator in column_name for indicator in pk_indicators)
            
            if is_likely_pk:
                columns_df.at[idx, 'column_group'] = 'primary key'
            else:
                columns_df.at[idx, 'column_group'] = 'source column'
        
        # TODO: Enhance with AI estimation for more accurate primary key detection
        
        return columns_df
