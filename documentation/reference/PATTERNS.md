# Established Patterns - DWH Creator

⚠️ **CRITICAL**: These patterns are already implemented. DO NOT RECREATE!

## Column ID Sequencing System
**Status**: ✅ IMPLEMENTED  
**Location**: `src/utils/column_cascading.py` line 1269  
**Method**: `ColumnCascadingEngine._get_next_column_id()`

### Pattern Details
- **Format**: `c1`, `c2`, `c3`, `c4`, `c5...` (sequential integers)
- **Logic**: Reads existing IDs, finds max, increments by 1
- **Global**: Maintains sequence across all artifacts and stages
- **Smart**: Handles existing data gracefully

### Usage
```python
from src.utils.column_cascading import ColumnCascadingEngine

engine = ColumnCascadingEngine(workbench_path, config_path)
column_id = engine._get_next_column_id()  # Returns "c1", "c2", etc.
```

### ❌ Don't Do This
```python
# DON'T recreate manual sequencing
column_id = f"C_{artifact_name}_{column_name}"  # Wrong!
column_id = f"c{counter}"  # Wrong - use established method!
```

---

## Artifact ID Convention
**Status**: ✅ ESTABLISHED  
**Pattern**: `a1`, `a2`, `a3`, `a4...`  
**Source**: Git template and existing workbench

### Details
- **Format**: `a` + sequential number
- **NOT**: `c1`, `c2` (those are for Column IDs)
- **NOT**: `T_customer` or descriptive names
- **Examples**: `a1` = customer, `a2` = product, `a3` = orders

---

## Artifact Naming Convention  
**Status**: ✅ ESTABLISHED  
**Pattern**: Clean names without suffixes

### Details
- **Correct**: `customer`, `product`, `orders`
- **Wrong**: `customer_table`, `product_table`
- **No suffixes**: Keep names simple and clean

---

## Stage ID References
**Status**: ✅ ESTABLISHED  
**Pattern**: `s0`, `s1`, `s2`, `s3`, `s4`, `s5`, `s6`

### Stage Mapping
- `s0` = `0_drop_zone` (source files)
- `s1` = `1_bronze` (raw ingestion)
- `s2` = `2_silver` (cleaned/standardized)
- `s3` = `3_gold` (business logic)
- `s4` = `4_mart` (aggregated)
- `s5` = `5_PBI_Model` (Power BI)
- `s6` = `5_PBI_Model` (KPI layer)

### Usage in Columns Sheet
- **stage_id**: Reference to stage (e.g., `s0`)
- **Stage Name**: Human readable (e.g., `0_drop_zone`)
- **Lookup**: stage_id links to Artifacts sheet for name resolution

---

## Column Group Classification
**Status**: ✅ ESTABLISHED  
**Pattern**: Minimal, specific values only

### Valid Values
- **"Primary Key"**: Only for actual primary key columns
- **""** (empty): For all other columns
- **NOT**: "Attribute", "Demographic", "Measure" (too detailed)

### Logic
```python
col_group = 'Primary Key' if column_name in primary_keys else ''
```

---

## Header Conventions
**Status**: ✅ ESTABLISHED  
**Pattern**: snake_case for technical fields, Title Case for display

### Examples
- **Technical**: `stage_id`, `artifact_id`, `column_id`
- **Display**: `Stage Name`, `Artifact Name`, `Column Name`
- **Mixed**: Follow existing workbench template exactly

---

## Workbench Structure
**Status**: ✅ ESTABLISHED  
**Sheets**: `Stages`, `Artifacts`, `Columns`

### Columns Sheet Structure (12 columns)
1. `stage_id` - Reference to stage
2. `Stage Name` - Human readable stage
3. `Artifact ID` - a1, a2, a3 format
4. `Artifact Name` - Clean name without suffix
5. `Column ID` - c1, c2, c3 format (use `_get_next_column_id()`)
6. `Column Name` - Original column name
7. `Order` - Column order within artifact
8. `Data Type` - SQL data type
9. `Column Comment` - Description
10. `Column Business Name` - User-friendly name
11. `Column Group` - Primary Key or empty
12. `Source Column` - Source file reference

---

## Data Type Mapping
**Status**: ✅ ESTABLISHED  
**Location**: `cascading_config_AdwentureWorks.xlsx`

### Common Mappings
- **int64**: `INTEGER`
- **float64**: `DECIMAL(10,2)`
- **object**: `VARCHAR(255)`
- **datetime**: `DATE` or `DATETIME`

---

## Primary Key Detection
**Status**: ✅ ESTABLISHED  
**Logic**: Based on column name patterns and data analysis

### Patterns
- **Single PK**: `cust_ID`, `prod_id`
- **Composite PK**: Multiple columns together
- **Detection**: Automated in `SourceFileAnalyzer`

---

## File Naming Conventions
**Status**: ✅ ESTABLISHED

### Workbench Files
- `workbench_[ProjectName].xlsx`
- `cascading_config_[ProjectName].xlsx`

### Source Files
- CSV files in `1_sources` directory
- Named clearly: `customer.csv`, `product.csv`, `orders.csv`

---

## ⚠️ NEVER RECREATE THESE MODULES

### Existing Functionality
- `ColumnCascadingEngine` - Complete column management
- `SourceFileAnalyzer` - CSV analysis and metadata
- `SourceFileIntegrator` - End-to-end integration
- `ExcelUtils` - Workbook manipulation
- `ConfigManager` - Configuration management

### Before Building New Features
1. Check existing modules first
2. Search codebase for similar functionality
3. Review Git history for established patterns
4. Ask: "Has this been solved already?"