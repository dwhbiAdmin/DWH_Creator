#!/usr/bin/env python3
"""
Test script for AI comment generation functionality
"""

import sys
import os
from pathlib import Path

# Add src to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from utils.ai_comment_generator import AICommentGenerator
from utils.app_config import AppConfig

def test_ai_comment_generation():
    """Test AI comment generation functionality."""
    print("🧪 Testing AI Comment Generation")
    print("=" * 40)
    
    # Initialize AI generator
    ai_generator = AICommentGenerator()
    
    if not ai_generator.is_available():
        print("❌ AI comment generation not available")
        print("💡 Please ensure OpenAI API key is configured in config/config.ini")
        return False
    
    print("✅ AI comment generator initialized successfully")
    
    # Test artifact comment generation
    print("\n📊 Testing artifact comment generation...")
    test_artifacts = [
        ("customer_bronze", "bronze"),
        ("sales_silver", "silver"),
        ("revenue_gold", "gold"),
        ("dashboard_mart", "mart")
    ]
    
    for artifact_name, stage_name in test_artifacts:
        try:
            comment = ai_generator.generate_artifact_comment(artifact_name, stage_name)
            print(f"  {artifact_name} ({stage_name}): {comment}")
        except Exception as e:
            print(f"  ❌ Error generating comment for {artifact_name}: {e}")
    
    # Test column comment generation
    print("\n📝 Testing column comment generation...")
    test_columns = [
        ("customer_id", "INTEGER", "customer_bronze"),
        ("order_date", "DATETIME", "orders_silver"),
        ("total_amount", "DECIMAL(10,2)", "sales_gold"),
        ("created_timestamp", "TIMESTAMP", "audit_log")
    ]
    
    for column_name, data_type, artifact_name in test_columns:
        try:
            comment = ai_generator.generate_column_comment(column_name, data_type, artifact_name)
            print(f"  {column_name} ({data_type}): {comment}")
        except Exception as e:
            print(f"  ❌ Error generating comment for {column_name}: {e}")
    
    print("\n✅ AI comment generation test completed")
    return True

if __name__ == "__main__":
    test_ai_comment_generation()
