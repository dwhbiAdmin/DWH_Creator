#!/usr/bin/env python3
"""
Test AI Column Generation
========================

Test script to verify the refactored AI functionality works correctly
with the new AI workbench manager.
"""

import sys
import os
from pathlib import Path

# Add src to path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from backend.project_manager import ProjectManager
from backend.workbench_manager import WorkbenchManager
from utils.config_manager import ConfigManager

def test_ai_functionality():
    """Test the AI functionality with a real project."""
    print("🧪 Testing AI Column Generation")
    print("=" * 50)
    
    # Get configuration
    config = ConfigManager()
    
    # Find existing project
    project_manager = ProjectManager()
    projects = project_manager.list_available_projects()
    
    if not projects:
        print("❌ No projects found to test with")
        print("💡 Create a project first using the console interface")
        return False
    
    # Use the first available project
    project = projects[0]
    project_path = project['path']
    print(f"📁 Using project: {project['name']}")
    print(f"📂 Path: {project_path}")
    
    # Initialize workbench manager
    print("\n🔧 Initializing workbench manager...")
    try:
        # Get OpenAI API key from config
        from utils.app_config import AppConfig
        app_config = AppConfig()
        api_key = app_config.get_openai_api_key()
        
        workbench_manager = WorkbenchManager(project_path, api_key)
        
        if not workbench_manager.workbook_path:
            print("❌ No workbook found in project")
            return False
        
        print(f"✅ Workbook found: {os.path.basename(workbench_manager.workbook_path)}")
        
        # Check AI availability
        print(f"\n🤖 AI Available: {workbench_manager.is_ai_available()}")
        
        if not workbench_manager.is_ai_available():
            print("❌ AI not available - check OpenAI API key configuration")
            return False
        
        # Get AI statistics before generation
        print("\n📊 AI Comment Statistics (Before):")
        stats_before = workbench_manager.get_ai_comment_statistics()
        print(f"  Artifacts: {stats_before.get('artifacts', {}).get('with_comments', 0)}/{stats_before.get('artifacts', {}).get('total', 0)} ({stats_before.get('artifacts', {}).get('coverage_percent', 0)}%)")
        print(f"  Columns: {stats_before.get('columns', {}).get('with_comments', 0)}/{stats_before.get('columns', {}).get('total', 0)} ({stats_before.get('columns', {}).get('coverage_percent', 0)}%)")
        
        # Test artifact AI comments
        print("\n🎯 Testing Artifact AI Comments...")
        artifact_success = workbench_manager.generate_artifact_ai_comments()
        print(f"  Result: {'✅ Success' if artifact_success else '❌ Failed'}")
        
        # Test column AI comments
        print("\n🎯 Testing Column AI Comments...")
        column_success = workbench_manager.generate_column_ai_comments()
        print(f"  Result: {'✅ Success' if column_success else '❌ Failed'}")
        
        # Get AI statistics after generation
        print("\n📊 AI Comment Statistics (After):")
        stats_after = workbench_manager.get_ai_comment_statistics()
        print(f"  Artifacts: {stats_after.get('artifacts', {}).get('with_comments', 0)}/{stats_after.get('artifacts', {}).get('total', 0)} ({stats_after.get('artifacts', {}).get('coverage_percent', 0)}%)")
        print(f"  Columns: {stats_after.get('columns', {}).get('with_comments', 0)}/{stats_after.get('columns', {}).get('total', 0)} ({stats_after.get('columns', {}).get('coverage_percent', 0)}%)")
        
        # Validate AI comments
        print("\n🔍 Validating AI Comments...")
        validation_results = workbench_manager.validate_ai_comments()
        
        if validation_results:
            artifacts_validation = validation_results.get('artifacts', {})
            columns_validation = validation_results.get('columns', {})
            
            print(f"  Artifact Comments:")
            print(f"    Valid: {artifacts_validation.get('valid', 0)}")
            print(f"    Too Short: {artifacts_validation.get('too_short', 0)}")
            print(f"    Empty: {artifacts_validation.get('empty', 0)}")
            
            print(f"  Column Comments:")
            print(f"    Valid: {columns_validation.get('valid', 0)}")
            print(f"    Too Short: {columns_validation.get('too_short', 0)}")
            print(f"    Empty: {columns_validation.get('empty', 0)}")
        
        print("\n🎉 AI functionality test completed!")
        return artifact_success and column_success
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting AI functionality test...\n")
    success = test_ai_functionality()
    
    print(f"\n{'🎉 Test PASSED' if success else '❌ Test FAILED'}")
    sys.exit(0 if success else 1)
