"""
AI Comment Generator for DWH Creator
===================================

Handles AI-powered comment generation for artifacts and columns using OpenAI API.
Adapted from previous implementation for DWH Creator specific needs.
"""

# ANCHOR: Imports and Dependencies

from openai import OpenAI
import os
from typing import Dict, List, Optional
from .Z_app_configurations import AppConfig

# ANCHOR: AICommentGenerator Class Definition


class AICommentGenerator:
    """Handles AI-powered comment generation for artifacts and columns."""
    
    # ANCHOR: Initialization and Setup
    def __init__(self, api_key: str = None):
        """
        Initialize the AI comment generator.
        
        Args:
            api_key: OpenAI API key. If not provided, will try to get from config/environment.
        """
        self.app_config = AppConfig()
        self.api_key = api_key or self.app_config.get_openai_api_key()
        self.model = self.app_config.get_openai_model()
        self.client = None
        
        if self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key)
            except Exception as e:
                print(f"Warning: Error initializing OpenAI client: {e}")
                self.client = None
    
    def generate_artifact_comment(self, artifact_name: str, stage_name: str = None) -> str:
        """
        Generate a comment for an artifact (table/view) using OpenAI API.
        
        Args:
            artifact_name: Name of the artifact
            stage_name: Stage name (bronze, silver, gold, etc.)
            
        Returns:
            Generated comment for the artifact
        """
        if not self.client:
            return ""  # Return empty if no AI available
        
        try:
            stage_context = f" in the {stage_name} stage" if stage_name else ""
            
            prompt = f"""
            You are a data warehouse expert. Generate a brief, professional description (max 120 characters) for this data warehouse artifact{stage_context}:
            
            Artifact Name: {artifact_name}
            Stage: {stage_name or 'Unknown'}
            
            Based on the artifact name and stage, explain what business data this artifact likely contains.
            Consider data warehouse layer purposes:
            - Bronze: Raw data ingestion
            - Silver: Cleaned and validated data
            - Gold: Business-ready aggregated data
            - Mart: Department-specific views
            
            Be specific about what kind of business information this artifact stores.
            
            Examples:
            - customer_bronze → "Raw customer data from source systems"
            - sales_silver → "Cleaned and validated sales transaction data"
            - revenue_gold → "Aggregated revenue metrics for reporting"
            """
            
            response = self.client.chat.completions.create(
                model=self.model,  # Using configurable model
                messages=[{"role": "user", "content": prompt}],
                max_tokens=80,
                temperature=0.3
            )
            
            comment = response.choices[0].message.content.strip()
            # Remove quotes if AI added them
            comment = comment.strip('"\'')
            return comment[:120]  # Limit length
            
        except Exception as e:
            print(f"AI API error for artifact {artifact_name}: {e}")
            return ""  # Return empty on error
    
    def generate_column_comment(self, column_name: str, data_type: str, artifact_name: str = None) -> str:
        """
        Generate a comment for a column using OpenAI API.
        
        Args:
            column_name: Name of the column
            data_type: Data type of the column
            artifact_name: Name of the parent artifact (optional)
            
        Returns:
            Generated comment for the column
        """
        if not self.client:
            return ""  # Return empty if no AI available
        
        try:
            prompt = f"""
            You are a data warehouse expert. Generate a brief, professional comment (max 80 characters) for this database column:
            
            Column Name: {column_name}
            Data Type: {data_type}
            Table: {artifact_name or 'Unknown'}
            
            Based on the column name and context, explain what this column likely represents in business terms.
            Look for common patterns in data warehouse column naming:
            - Technical columns (created_timestamp, batch_id, source_system)
            - Business keys (customer_id, product_code)
            - Surrogate keys (sk_, _key suffixes)
            - Measures and facts (amount, quantity, count)
            - Attributes (name, status, type)
            
            Be concise and business-focused.
            
            Examples:
            - customer_id (integer) → "Customer unique identifier"
            - order_date (datetime) → "Date when order was placed"
            - total_amount (decimal) → "Total monetary amount"
            - created_timestamp (timestamp) → "Record creation timestamp"
            """
            
            response = self.client.chat.completions.create(
                model=self.model,  # Using configurable model
                messages=[{"role": "user", "content": prompt}],
                max_tokens=50,
                temperature=0.3
            )
            
            comment = response.choices[0].message.content.strip()
            # Remove quotes if AI added them
            comment = comment.strip('"\'')
            return comment[:80]  # Limit length
            
        except Exception as e:
            print(f"AI API error for column {column_name}: {e}")
            return ""  # Return empty on error
    
    def generate_readable_column_name(self, column_name: str, data_type: str) -> str:
        """
        Generate a human-readable column name for business artifacts.
        
        Args:
            column_name: Technical column name
            data_type: Data type of the column
            
        Returns:
            Human-readable column name
        """
        if not self.client:
            return ""  # Return empty if no AI available
        
        try:
            prompt = f"""
            Convert this technical database column name into a business-friendly snake_case name for data warehouse gold layer:
            
            Technical Name: {column_name}
            Data Type: {data_type}
            
            Rules:
            - Use snake_case (lowercase with underscores)
            - Keep "id" as "id", never use "identifier"
            - Make business-friendly but concise
            - Avoid technical jargon and cryptic abbreviations
            - Maximum 50 characters
            - Return ONLY the column name, no prefixes or explanations
            
            Examples:
            - cust_id → customer_id
            - order_dt → order_date
            - total_amt → total_amount
            - prod_cat_cd → product_category_code
            - created_ts → created_timestamp
            - CUST_FIRST_NM → customer_first_name
            - ORD_STS_CD → order_status_code
            - SALES_AMT_USD → sales_amount_usd
            - emp_id → employee_id
            - acct_id → account_id
            """
            
            response = self.client.chat.completions.create(
                model=self.model,  # Using configurable model
                messages=[{"role": "user", "content": prompt}],
                max_tokens=30,
                temperature=0.3
            )
            
            readable_name = response.choices[0].message.content.strip()
            # Clean up the response - remove quotes, prefixes, and extra text
            readable_name = readable_name.strip('"\'')
            
            # Remove common AI response prefixes and unwanted text
            prefixes_to_remove = [
                "Business-Friendly Name:", 
                "Business Name:", 
                "Readable Name:",
                "Column Name:",
                "Name:",
                "Business-Friendly Name",
                "→",
                "->",
                "Output:",
                "Result:"
            ]
            
            for prefix in prefixes_to_remove:
                if readable_name.startswith(prefix):
                    readable_name = readable_name[len(prefix):].strip()
                    break
            
            # Remove quotes and extra characters again after prefix removal
            readable_name = readable_name.strip('"\'()[]{}')
            
            # Ensure it follows snake_case and replace "identifier" with "id"
            readable_name = readable_name.lower().replace(" ", "_")
            readable_name = readable_name.replace("identifier", "id")
            readable_name = readable_name.replace("_id_", "_id")  # Avoid double id
            
            return readable_name[:50]  # Limit length
            
        except Exception as e:
            print(f"AI API error for readable name {column_name}: {e}")
            return ""  # Return empty on error
    
    def generate_business_names_batch(self, columns_data: List[Dict]) -> Dict[str, str]:
        """
        Generate business names for multiple columns efficiently.
        
        Args:
            columns_data: List of dictionaries with 'column_name' and 'data_type' keys
            
        Returns:
            Dictionary mapping column names to business names
        """
        business_names = {}
        
        if not self.client:
            return business_names  # Return empty if no AI available
        
        # Process columns in batches to avoid API limits
        for column_data in columns_data:
            column_name = column_data.get('column_name', '')
            data_type = column_data.get('data_type', '')
            
            if column_name:
                business_name = self.generate_readable_column_name(column_name, data_type)
                if business_name:
                    business_names[column_name] = business_name
        
        return business_names
    
    def is_available(self) -> bool:
        """
        Check if AI functionality is available.
        
        Returns:
            bool: True if AI client is initialized and ready
        """
        return self.client is not None
