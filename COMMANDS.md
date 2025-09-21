# Common Commands - DWH Creator

Quick reference for frequently used commands and code patterns.

## Session Startup Commands

### Check Project Status
```bash
# Git status and recent commits
git status
git log --oneline -5

# Check current branch
git branch

# See what changed recently  
git diff --stat HEAD~1
```

### Check Current Workbench State
```python
import pandas as pd

workbench_path = r"c:\Users\bezas\repos\DWH_Creator\_DWH_Projects\Project_AdwentureWorks\2_workbench\workbench_AdwentureWorks.xlsx"

# Quick workbench overview
df_columns = pd.read_excel(workbench_path, sheet_name='Columns')
df_artifacts = pd.read_excel(workbench_path, sheet_name='Artifacts')

print(f"Columns: {len(df_columns)} rows")
print(f"Column IDs: {df_columns['Column ID'].head(10).tolist()}")
print(f"Artifacts: {len(df_artifacts)} total")
print(f"Source artifacts: {len(df_artifacts[df_artifacts['Stage ID'] == 's0'])}")
```

---

## Established Column ID Sequencing

### Use Existing System (✅ CORRECT)
```python
from src.utils.column_cascading import ColumnCascadingEngine

workbench_path = r"c:\Users\bezas\repos\DWH_Creator\_DWH_Projects\Project_AdwentureWorks\2_workbench\workbench_AdwentureWorks.xlsx"
config_path = r"c:\Users\bezas\repos\DWH_Creator\_DWH_Projects\Project_AdwentureWorks\2_workbench\cascading_config_AdwentureWorks.xlsx"

# Initialize engine
engine = ColumnCascadingEngine(workbench_path, config_path)

# Get next column ID (c1, c2, c3...)
column_id = engine._get_next_column_id()
```

### ❌ Don't Do This (Manual Sequencing)
```python
# WRONG - Don't recreate existing functionality
column_id = f"c{counter}"  
column_id = f"C_{artifact_name}_{column_name}"
```

---

## Column Data Population

### Standard Column Row Creation
```python
# Use this pattern for creating column rows
column_data = [
    's0',                                   # stage_id
    '0_drop_zone',                         # Stage Name  
    artifact_id,                           # Artifact ID (a1, a2, a3...)
    artifact_name,                         # Artifact Name (no _table suffix)
    engine._get_next_column_id(),          # Column ID (c1, c2, c3...)
    column_name,                           # Column Name
    order_idx,                             # Order
    data_type,                             # Data Type
    f'{business_name} from {artifact_name} source file',  # Column Comment
    business_name,                         # Column Business Name
    'Primary Key' if is_pk else '',        # Column Group
    f'{csv_file}:{column_name}'            # Source Column
]
```

---

## Data Type Mapping

### Standard Data Type Logic
```python
def get_data_type(pandas_dtype, column_name):
    """Map pandas dtype to SQL data type."""
    dtype = str(pandas_dtype)
    
    if dtype.startswith('int'):
        return 'INTEGER'
    elif dtype.startswith('float'):
        return 'DECIMAL(10,2)'
    elif 'date' in column_name.lower():
        return 'DATE'
    else:
        return 'VARCHAR(255)'
```

---

## Primary Key Detection

### Simple PK Logic
```python
# Define primary keys per file
primary_keys_config = {
    'customer.csv': ['cust_ID'],
    'product.csv': ['prod_id', 'clr_id'],  # Composite key
    'orders.csv': ['cust_ID', 'prod_id', 'clr_id']  # Composite key
}

# Check if column is primary key
is_pk = column_name in primary_keys_config.get(csv_file, [])
column_group = 'Primary Key' if is_pk else ''
```

---

## Excel Workbook Operations

### Safe Excel Reading/Writing
```python
import openpyxl
import pandas as pd

# Read with pandas (for data analysis)
df = pd.read_excel(workbench_path, sheet_name='Columns')

# Write with openpyxl (for precise control)
wb = openpyxl.load_workbook(workbench_path)
ws = wb['Columns']

# Clear sheet
ws.delete_rows(1, ws.max_row)

# Write data
for row_num, row_data in enumerate(data, 1):
    for col_num, value in enumerate(row_data, 1):
        ws.cell(row=row_num, column=col_num, value=value)

# Apply formatting
ws.freeze_panes = 'A2'
ws.auto_filter.ref = ws.dimensions

# Save
wb.save(workbench_path)
```

---

## File Path Configuration

### Standard Paths
```python
# Project paths
project_root = r"c:\Users\bezas\repos\DWH_Creator"
project_dir = r"c:\Users\bezas\repos\DWH_Creator\_DWH_Projects\Project_AdwentureWorks"

# Workbench files
workbench_path = f"{project_dir}\\2_workbench\\workbench_AdwentureWorks.xlsx"
config_path = f"{project_dir}\\2_workbench\\cascading_config_AdwentureWorks.xlsx"

# Source files
csv_dir = f"{project_dir}\\1_sources"
csv_files = ['customer.csv', 'product.csv', 'orders.csv']
```

---

## Complete Column Processing Workflow

### Full CSV to Workbench Process
```python
from src.utils.column_cascading import ColumnCascadingEngine
import pandas as pd
import openpyxl

# 1. Initialize
engine = ColumnCascadingEngine(workbench_path, config_path)

# 2. Clear and set up workbench
wb = openpyxl.load_workbook(workbench_path)
ws_columns = wb['Columns']
ws_columns.delete_rows(1, ws_columns.max_row)

# Headers
headers = ['stage_id', 'Stage Name', 'Artifact ID', 'Artifact Name', 'Column ID', 
          'Column Name', 'Order', 'Data Type', 'Column Comment', 'Column Business Name', 
          'Column Group', 'Source Column']

for col_num, header in enumerate(headers, 1):
    ws_columns.cell(row=1, column=col_num, value=header)

# 3. Process each CSV
row_counter = 2
for csv_file, config in csv_files_config.items():
    df = pd.read_csv(f"{csv_dir}\\{csv_file}", delimiter=';')
    
    for order_idx, column_name in enumerate(df.columns, 1):
        # Create column row using established patterns
        column_data = [
            's0', '0_drop_zone', config['artifact_id'], config['artifact_name'],
            engine._get_next_column_id(),  # Use established sequencing
            column_name, order_idx, get_data_type(df[column_name].dtype, column_name),
            f"{business_name} from {config['artifact_name']} source file",
            business_name, 'Primary Key' if is_pk else '', f"{csv_file}:{column_name}"
        ]
        
        # Write to Excel
        for col_num, value in enumerate(column_data, 1):
            ws_columns.cell(row=row_counter, column=col_num, value=value)
        row_counter += 1

# 4. Save
ws_columns.freeze_panes = 'A2'
ws_columns.auto_filter.ref = ws_columns.dimensions
wb.save(workbench_path)
```

---

## Verification Commands

### Verify Column Structure
```python
# Check if column IDs follow c1, c2, c3 pattern
df = pd.read_excel(workbench_path, sheet_name='Columns')
column_ids = df['Column ID'].dropna().tolist()
proper_format = all(str(cid).startswith('c') and str(cid)[1:].isdigit() for cid in column_ids)

print(f"Total columns: {len(df)}")
print(f"Column IDs: {column_ids}")
print(f"Proper format: {proper_format}")
print(f"Primary keys: {len(df[df['Column Group'] == 'Primary Key'])}")
```

### Verify Artifact Structure
```python
df_artifacts = pd.read_excel(workbench_path, sheet_name='Artifacts')
source_artifacts = df_artifacts[df_artifacts['Stage ID'] == 's0']

print(f"Total artifacts: {len(df_artifacts)}")
print(f"Source artifacts: {len(source_artifacts)}")
print(f"Source artifact IDs: {source_artifacts['Artifact ID'].tolist()}")
print(f"Source artifact names: {source_artifacts['Artifact Name'].tolist()}")
```

---

## Git Workflow Commands

### Session End Git Commands
```bash
# Check what changed
git status
git diff --name-only

# Add and commit with detailed message
git add .
git commit -m "feat: Fix workbench column structure using established sequencing

- Apply c1,c2,c3 column ID format from ColumnCascadingEngine._get_next_column_id()
- Fix stage_id to reference s0 for 0_drop_zone  
- Use a1,a2,a3 artifact convention (no _table suffix)
- Column Group only shows 'Primary Key' for PKs
- All 13 columns processed correctly

Resolves: Column structure inconsistencies
Files: workbench_AdwentureWorks.xlsx"

# Push changes
git push origin main
```

---

## Troubleshooting Commands

### Check Module Imports
```python
# Verify modules are available
try:
    from src.utils.column_cascading import ColumnCascadingEngine
    print("✓ ColumnCascadingEngine available")
except ImportError as e:
    print(f"✗ Import error: {e}")

try:
    from src.utils.source_file_integrator import SourceFileIntegrator  
    print("✓ SourceFileIntegrator available")
except ImportError as e:
    print(f"✗ Import error: {e}")
```

### Check File Existence
```python
import os

files_to_check = [
    workbench_path,
    config_path,
    f"{csv_dir}\\customer.csv",
    f"{csv_dir}\\product.csv", 
    f"{csv_dir}\\orders.csv"
]

for file_path in files_to_check:
    exists = os.path.exists(file_path)
    print(f"{'✓' if exists else '✗'} {file_path}")
```