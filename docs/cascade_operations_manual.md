# Cascade Operations Manual

## Overview

The Cascade Operations system automatically propagates column definitions from upstream artifacts to downstream artifacts across different stages of the data warehouse pipeline. This manual documents the implementation completed on October 12, 2025.

## System Architecture

### Pipeline Stages

The data warehouse follows a multi-stage architecture:

1. **s0 (drop_zone)** - Raw data landing zone
2. **s1 (bronze)** - Initial data ingestion
3. **s2 (silver)** - Cleansed and conformed data
4. **s3 (gold)** - Business-ready aggregated data
5. **s4 (mart)** - Department-specific data marts
6. **s5 (PBI_Model)** - Power BI semantic models
7. **s6 (PBI_Reports)** - Power BI reporting layer

### Folder Structure

```
src/backend/_2_Workbench/
├── _1_import_raw_fields/     # Raw field import operations
└── _2_cascade_fields/         # Cascade operations
    ├── a_cascade_operations.py      # Main cascade engine
    └── b_cascade_enhancements.py    # Post-processing cleanup
```

## Component 1: a_cascade_operations.py

### Purpose
Main cascade engine that propagates columns from upstream artifacts to downstream artifacts based on configured relationships.

### Key Functions

#### 1. cascade_main()
**Purpose:** Entry point that iterates through all artifacts and initiates cascading.

**Process:**
1. Reads the `artifacts` sheet from the workbook
2. For each artifact, retrieves its stage information
3. Calls `cascade_engine()` to process upstream relationships
4. Logs progress and completion

**Usage:**
```python
from a_cascade_operations import cascade_main
cascade_main()
```

#### 2. cascade_engine(artifact_id, artifact_name, stage_id, upstream_artifact)
**Purpose:** Core cascading logic that handles column propagation from upstream artifacts.

**Parameters:**
- `artifact_id`: Target artifact identifier (e.g., "a12")
- `artifact_name`: Target artifact name
- `stage_id`: Target stage identifier (e.g., "s2")
- `upstream_artifact`: Source artifact(s) to cascade from (can be comma-separated)

**Process:**
1. Validates upstream_artifact is not empty
2. Splits multiple upstream artifacts by comma
3. For each upstream artifact:
   - Retrieves upstream stage information
   - Determines artifact_side (source vs business)
   - Calls `_process_upstream_artifact()` for actual cascading

### Artifact Side Logic

#### Source-Side Artifacts
When both upstream and downstream artifacts have `artifact_side = "source"`:

- **Column Names:** Preserved as-is from `column_name`
- **Data Types:** No conversion, copied directly
- **Column Order:** Incremented by +100 from upstream

**Use Case:** Technical/system columns in bronze and silver layers

#### Business-Side Artifacts  
When upstream has `artifact_side = "business"`:

- **Column Names:** Uses `column_business_name` (with fallback to `column_name`)
- **Data Types:** Converted to target platform using `conf_4_data_mappings`
- **Column Order:** Special handling (see Fix 3 below)

**Use Case:** Business-friendly columns in gold, mart, and Power BI layers

## Critical Fixes Implemented

### Fix 1: NaN Handling for Business Names

**Problem:** Artifacts a13-a19 had `column_name = NaN` after cascading from business-side upstreams because `column_business_name` was empty.

**Solution:** Implemented fallback logic with pandas NaN checking.

**Code Location:** Lines 246-250 in `_process_upstream_artifact()`

```python
if pd.notna(upstream_row['column_business_name']) and str(upstream_row['column_business_name']).strip():
    target_column_name = upstream_row['column_business_name']
else:
    target_column_name = upstream_row['column_name']
```

**Impact:** Ensures all cascaded columns have valid names, preventing NaN assignments.

---

### Fix 2: Duplicate Prevention for Multiple Upstreams

**Problem:** When multiple upstream artifacts existed (e.g., a12 with "a10, a11"), duplicate `column_name` entries were created because cascading processed each upstream independently.

**Solution:** Track existing columns across all upstream iterations and skip duplicates.

**Code Location:** Lines 209-242 in `_process_upstream_artifact()`

```python
# Get existing columns before cascading
existing_columns = columns_df[columns_df['artifact_id'] == artifact_id]
existing_columns_in_artifact = existing_columns['column_name'].tolist()

# During cascading loop
if target_column_name in existing_columns_in_artifact:
    continue  # Skip duplicate
    
# After successful insert
existing_columns_in_artifact.append(target_column_name)
```

**Impact:** 
- Artifact a12: Prevented 3 duplicates
- Artifact a18: Prevented 8 duplicates
- Total duplicates prevented: 11 across all artifacts

---

### Fix 3: Attribute Column Ordering

**Problem:** Attribute columns (keys, flags, metadata) needed consistent ordering starting at 100, but the standard logic added +100 to upstream order, causing gaps and inconsistency.

**Solution:** Special ordering logic for `column_group = 'attribute'`.

**Code Location:** Lines 270-277 in `_process_upstream_artifact()`

```python
upstream_column_group = upstream_row['column_group']
if pd.notna(upstream_column_group) and str(upstream_column_group).strip().lower() == 'attribute':
    target_order = attribute_order_counter
    attribute_order_counter += 1
else:
    target_order = upstream_row['order'] + 100
```

**Logic:**
- **Attributes:** Start at order 100, increment by +1 (100, 101, 102...)
- **Non-attributes:** Use original order + 100

**Impact:** Consistent, sequential ordering for key and metadata columns.

---

## Component 2: b_cascade_enhancements.py

### Purpose
Post-processing operations to clean up and restructure cascaded data.

### Key Functions

#### 1. cleanup_delete_duplicate_rows()
**Purpose:** Removes duplicate column entries within each artifact.

**Process:**
1. Reads the `columns` sheet
2. Uses pandas `drop_duplicates()` on `['artifact_id', 'column_name']`
3. Keeps first occurrence of each duplicate
4. Saves cleaned data back to workbook

**Usage:**
```python
from b_cascade_enhancements import cleanup_delete_duplicate_rows
cleanup_delete_duplicate_rows()
```

**Test Results:** Successfully removed 11 duplicates, reducing 104 columns to 93.

#### 2. reenumerate_column_ids()
**Purpose:** Renumbers all `column_id` values sequentially (c_1, c_2, c_3...).

**Process:**
1. Reads the `columns` sheet
2. Sorts by appropriate criteria (artifact_id, order)
3. Assigns sequential IDs starting from c_1
4. Updates workbook with new IDs

**Note:** This function is defined but should be called after all cascading is complete.

---

## Data Type Conversion

The system supports platform-specific data type conversion using the `conf_4_data_mappings` sheet:

| Source Platform | Target Platform | Example Mapping |
|----------------|-----------------|-----------------|
| SQL Server | Databricks | `nvarchar(50)` → `string` |
| SQL Server | Power BI | `int` → `Whole Number` |
| Databricks | Power BI | `decimal(10,2)` → `Decimal Number` |

**Configuration:** Mappings are defined in the `conf_4_data_mappings` sheet with columns:
- `source_platform`
- `source_data_type`
- `target_platform`
- `target_data_type`

---

## Execution Workflow

### Standard Cascade Operation

1. **Prepare Workbook:** Ensure `artifacts`, `stages`, `columns`, and `conf_4_data_mappings` sheets are configured
2. **Run Cascade:** Execute `cascade_main()` from `a_cascade_operations.py`
3. **Review Results:** Check cascaded columns in each downstream artifact
4. **Run Cleanup:** Execute `cleanup_delete_duplicate_rows()` if duplicates exist
5. **Reenumerate:** Run `reenumerate_column_ids()` to standardize IDs

### Testing Workflow

For testing purposes, you can clear cascaded columns:

```python
# cleanup_test.py - Deletes all cascaded columns for fresh testing
import pandas as pd
from openpyxl import load_workbook

# Delete cascaded columns where upstream_artifact is not null
df = df[df['upstream_artifact'].isna() | (df['upstream_artifact'] == '')]
```

---

## Configuration Requirements

### artifacts Sheet
Required columns:
- `artifact_id`: Unique identifier (a1, a2, a3...)
- `artifact_name`: Descriptive name
- `stage_id`: Associated stage (s0-s6)
- `upstream_artifact`: Comma-separated source artifacts (e.g., "a10, a11")

### stages Sheet
Required columns:
- `stage_id`: Stage identifier
- `stage_name`: Stage name
- `artifact_side`: "source" or "business"
- `platform`: "SQL Server", "Databricks", "Power BI"

### columns Sheet
Required columns:
- `column_id`: Unique identifier (c_1, c_2...)
- `artifact_id`: Parent artifact
- `column_name`: Technical column name
- `column_business_name`: Business-friendly name
- `data_type`: Platform-specific data type
- `order`: Column ordering number
- `column_group`: Classification (e.g., "attribute", "measure")
- `upstream_artifact`: Source artifact (populated during cascade)

---

## Testing & Validation

### Test Case: Project_AW_Sales

**Configuration:**
- 19 artifacts (a1-a19) across 6 stages
- Multiple upstream relationships

**Results:**
| Stage | Artifacts | Initial Columns | After Cascade | After Cleanup |
|-------|-----------|----------------|---------------|---------------|
| s0    | a1-a5     | 13             | 13            | 13            |
| s1    | a6-a9     | 13             | 13            | 13            |
| s2    | a10-a13   | 13             | 13            | 13            |
| s3    | a14-a16   | 21             | 21            | 21            |
| s4    | a17       | 21             | 21            | 21            |
| s5    | a18-a19   | 29             | 104           | 93            |

**Validation Points:**
- ✅ No NaN column names (Fix 1 working)
- ✅ No duplicate columns after cleanup (Fix 2 working)
- ✅ Attributes ordered 100-106 sequentially (Fix 3 working)
- ✅ Data types converted correctly per platform
- ✅ 11 duplicates successfully removed

---

## Troubleshooting

### Issue: NaN Column Names
**Symptom:** Cascaded columns have `column_name = NaN`  
**Cause:** Empty `column_business_name` in business-side artifacts  
**Solution:** Fix 1 implemented - fallback to `column_name`

### Issue: Duplicate Columns
**Symptom:** Multiple identical `column_name` entries in same artifact  
**Cause:** Multiple upstream artifacts cascade same columns  
**Solution:** Fix 2 implemented - duplicate tracking across upstreams  
**Cleanup:** Run `cleanup_delete_duplicate_rows()`

### Issue: Inconsistent Attribute Ordering
**Symptom:** Attribute columns have scattered order numbers  
**Cause:** Standard +100 logic doesn't work for attributes  
**Solution:** Fix 3 implemented - sequential ordering starting at 100

### Issue: Wrong Data Types
**Symptom:** Data types don't match target platform  
**Cause:** Missing or incorrect mappings in `conf_4_data_mappings`  
**Solution:** Add/correct mapping entries for source→target platform combination

---

## Best Practices

1. **Always run cleanup after cascading** when multiple upstream artifacts exist
2. **Test with small datasets first** before cascading large workbooks
3. **Back up workbooks** before running cascade operations
4. **Review conf_4_data_mappings** before cascading across platforms
5. **Use reenumerate_column_ids** as final step to ensure sequential IDs
6. **Check logs** for any warnings or errors during cascade execution

---

## Future Enhancements

Potential improvements for future versions:

- [ ] Cascade pattern support (main, get_key, lookup, pbi)
- [ ] Incremental cascading (only update changed columns)
- [ ] Cascade validation rules and constraints
- [ ] Automated testing framework
- [ ] Performance optimization for large workbooks (1000+ artifacts)
- [ ] Column lineage tracking and visualization

---

## Version History

**Version 1.0 - October 12, 2025**
- Initial implementation of cascade_main and cascade_engine
- Source-side vs business-side artifact handling
- Fix 1: NaN handling with fallback logic
- Fix 2: Duplicate prevention for multiple upstreams
- Fix 3: Attribute column sequential ordering
- Post-processing cleanup and reenumeration functions
- Tested with Project_AW_Sales (19 artifacts, 93 final columns)

---

## Support & Maintenance

**Location:** `src/backend/_2_Workbench/_2_cascade_fields/`

**Key Files:**
- `a_cascade_operations.py` - Main cascade engine (460 lines)
- `b_cascade_enhancements.py` - Post-processing utilities

**Dependencies:**
- pandas (DataFrame operations)
- openpyxl (Excel manipulation)
- Custom utilities: ExcelUtils, Logger

**Branch:** session-2025-10-12 (ready for merge to main)

---

*End of Manual*
