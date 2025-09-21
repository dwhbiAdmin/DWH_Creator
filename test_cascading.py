# Test the complete cascading workflow with aligned naming conventions

import sys
sys.path.append('.')

from src.workbench.workbench_manager import WorkbenchManager

# Initialize the workbench
workbench_path = r"c:\Users\bezas\repos\DWH_Creator\_DWH_Projects\Project_AdwentureWorks\2_workbench\workbench_AdwentureWorks.xlsx"

print("=== TESTING COMPLETE CASCADING WORKFLOW ===")
print()

try:
    # Initialize workbench manager
    wb_manager = WorkbenchManager(workbench_path)
    
    print("✅ Workbench manager initialized successfully")
    print()
    
    # Run the cascading for all missing artifacts
    print("🔄 Starting complete cascading workflow...")
    print()
    
    result = wb_manager.column_cascader.cascade_all_missing_artifacts()
    
    if result:
        print("✅ CASCADING COMPLETE - SUCCESS!")
        print()
        
        # Show summary of what was cascaded
        columns_df = wb_manager.get_columns_data()
        
        print("=== CASCADING SUMMARY ===")
        print(f"Total columns in workbook: {len(columns_df)}")
        
        # Group by artifact to show distribution
        artifact_counts = columns_df.groupby('artifact_id').size().reset_index(name='column_count')
        
        print()
        print("Columns per artifact:")
        for _, row in artifact_counts.iterrows():
            print(f"  {row['artifact_id']}: {row['column_count']} columns")
            
        print()
        print("=== WORKFLOW VALIDATION COMPLETE ===")
        
    else:
        print("❌ CASCADING FAILED")
        print("Check the error details above")
        
except Exception as e:
    print(f"❌ Error during cascading workflow: {e}")
    import traceback
    traceback.print_exc()

print()
print("=== TEST COMPLETE ===")