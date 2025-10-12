"""
Run only the cleanup duplicate columns method on existing workbook
"""
import sys
from pathlib import Path

# Add src directory to path
current_dir = Path(__file__).parent
src_dir = current_dir / 'src'
sys.path.insert(0, str(src_dir))

from backend._2_Workbench._2_cascade_fields.a_cascade_operations import CascadeOperations

# Path to workbook
workbook_path = r"_DWH_Projects\Project_AW_sales\2_workbench\workbench_AW_Sales.xlsx"

# Create cascade operations instance
cascade_ops = CascadeOperations(workbook_path)

# Run only the cleanup method
print("Running cleanup to remove duplicate columns...")
cascade_ops._cleanup_duplicate_columns()
print("Cleanup completed!")
