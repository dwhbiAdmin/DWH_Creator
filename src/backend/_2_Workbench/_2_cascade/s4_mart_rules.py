"""
Stage s4 - Mart Cascade Rules
===============================
Rules from CASCADE_and_OTHER_RULES.xlsx - Cascading_Rules sheet
"""

import pandas as pd
from typing import Dict, List, Optional


class S4MartRules:
    """Implements cascade rules for s4 (4_mart) stage."""
    
    def __init__(self):
        self.stage_id = "s4"
        self.stage_name = "4_mart"
    
    def rule_mrt_1_field_selection(
        self,
        upstream_columns_df: pd.DataFrame,
        target_columns_df: pd.DataFrame,
        artifact_id: str
    ) -> pd.DataFrame:
        """
        Rule mrt-1: Field Selection
        
        Description: Take ALL fields from upstream (s3)
        Applies to: All artifacts
        """
        # Get existing column names in target artifact
        existing_columns = target_columns_df[
            target_columns_df['artifact_id'] == artifact_id
        ]['column_name'].tolist()
        
        # Filter out duplicates
        new_columns = upstream_columns_df[
            ~upstream_columns_df['column_name'].isin(existing_columns)
        ].copy()
        
        return new_columns
