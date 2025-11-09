# Cascade Rules Testing Guide - November 10, 2025

## Overview
New stage-specific cascade rules module has been implemented and merged to main branch.

## What's Ready for Testing

### ✅ Merged to Main Branch
- All changes from `br_cascade_focus_09_11_2025` have been merged to `main`
- Pushed to remote repository
- Ready for testing

### 📁 New Module Structure
```
src/backend/_2_Workbench/_2_cascade/
├── __init__.py
├── README.md
├── s0_drop_zone_rules.py    (2 rules)
├── s1_bronze_rules.py       (8 rules)
├── s2_silver_rules.py       (7 rules)
├── s3_gold_rules.py         (9 rules)
├── s4_mart_rules.py         (1 rule)
└── s5_powerbi_model_rules.py (placeholder)
```

### 📊 Source of Truth
- **CASCADE_and_OTHER_RULES.xlsx** - Contains all cascade rules specifications
- Located in project root directory

### 🔄 Key Changes
1. **Column Positions Updated** - New fields moved to columns L-P:
   - Column L: `source_column_name`
   - Column M: `lookup_fields`
   - Column N: `etl_simple_trnasformation`
   - Column O: `ai_transformation_prompt`
   - Column P: `etl_ai_transformation`

2. **Files Updated:**
   - `src/utils/a_project_setup_default_Workbench_utils.py`
   - `src/utils/a_project_setup_utils.py`
   - `src/backend/_2_Workbench/_2_cascade_fields/b_cascade_enhancements.py`
   - `src/utils/c_workbench_3_cascade_utils.py`

## Testing Checklist

### Stage 0 - Drop Zone
- [ ] Test AI estimation for data types and business names (rule drp-1)
- [ ] Test AI estimation for primary keys (rule drp-2)
- [ ] Verify columns with ID/PK are identified as primary keys

### Stage 1 - Bronze
- [ ] Test field selection from s0 (rule brz-1)
- [ ] Verify source naming preservation (rule brz-2)
- [ ] Test source_column_name = column_name (rule brz-3)
- [ ] Test all fields set to STRING except technical/partition (rule brz-4)
- [ ] Test order starts from 1 (rule brz-5)
- [ ] Test business name AI estimation (rule brz-6)
- [ ] Verify technical fields added correctly (rule brz-7):
  - __SourceSystem
  - __SourceFileName
  - __SourceFilePath
  - __1_bronze_insert_dt
  - __1_bronze_Partition_InsertYear
  - __1_bronze_Partition_InsertMonth
  - __1_bronze_Partition_insertDate
- [ ] Test other fields set correctly (rule brz-8)

### Stage 2 - Silver
- [ ] Test field selection excludes partition fields (rule slv-1)
- [ ] Test primary key fields creation with _PK suffix (rule slv-2)
- [ ] Verify technical fields added (rule slv-3):
  - __SourceSystem
  - __SourceFileName
  - __SourceFilePath
  - __1_bronze_insert_dt
  - __2_silver_last_update_dt
- [ ] Test source naming (rule slv-4)
- [ ] Test data types from s0 with platform conversion (rule slv-5)
- [ ] Test source_column_name = column_name (rule slv-6)
- [ ] Test other fields with PK handling (rule slv-7)

### Stage 3 - Gold
- [ ] Test field selection from s2 main relation (rule gld-1)
- [ ] Test dimension SK creation (rule gld-2)
- [ ] Test fact SKs for get_key relations (rule gld-3)
- [ ] Test dimension BK creation with empty data type (rule gld-4)
- [ ] Test fact BKs for get_key relations (rule gld-5)
- [ ] Verify technical field added (rule gld-6):
  - __3_gold_last_update_dt
- [ ] Test business naming strategy (rule gld-7)
- [ ] Test data types from s2 (rule gld-8)
- [ ] Test source columns from s2 (rule gld-9)

### Stage 4 - Mart
- [ ] Test field selection from s3 (rule mrt-1)

### Column Structure Verification
- [ ] Verify column order in Excel:
  - Columns A-K: Original fields
  - Column L: source_column_name
  - Column M: lookup_fields
  - Column N: etl_simple_trnasformation
  - Column O: ai_transformation_prompt
  - Column P: etl_ai_transformation
- [ ] Test new workbook creation with correct column structure
- [ ] Verify cascade operations populate new fields correctly

## Import and Usage

```python
# Import stage rules
from backend._2_Workbench._2_cascade import (
    S0DropZoneRules,
    S1BronzeRules,
    S2SilverRules,
    S3GoldRules,
    S4MartRules,
    S5PowerBIModelRules
)

# Example: Test Bronze rules
bronze_rules = S1BronzeRules()

# Test field selection
new_columns = bronze_rules.rule_brz_1_field_selection(
    upstream_columns_df=s0_columns,
    target_columns_df=s1_columns,
    artifact_id='test_artifact'
)
```

## Test Data Setup

### Required DataFrames for Testing:
1. **s0_columns_df** - Drop zone columns
2. **s1_columns_df** - Bronze stage columns
3. **s2_columns_df** - Silver stage columns
4. **s3_columns_df** - Gold stage columns
5. **artifacts_df** - Artifact definitions with relationships
6. **data_mappings_df** - Platform data type mappings (optional)

## Known Items to Address

1. **AI Estimation** - Rules drp-1, drp-2, brz-6 have TODO placeholders for AI integration
2. **Platform Conversion** - Rule slv-5 needs data_mappings_df integration testing
3. **Stage s5** - PowerBI Model rules not yet defined in CASCADE_and_OTHER_RULES.xlsx

## Success Criteria

✅ All rules execute without errors
✅ Column structure matches CASCADE_and_OTHER_RULES.xlsx specifications
✅ New fields (L-P) populated correctly
✅ Technical fields added in correct order
✅ Primary keys identified and _PK fields created
✅ SK/BK fields created for dimensions and facts
✅ Business naming applied at gold stage
✅ No duplicate columns created

## Rollback Plan (if needed)

```bash
# If issues found, can revert to previous state
git log --oneline -5  # Find commit before merge
git reset --hard <commit-hash>  # Replace with commit hash
git push --force origin main  # Force push (use with caution)
```

## Next Steps After Testing

1. Review test results
2. Fix any issues identified
3. Complete AI integration for estimation rules
4. Add s5 PowerBI Model rules when specifications available
5. Create integration tests
6. Update documentation with test results

---
**Date Prepared:** November 9, 2025
**Branch Merged:** br_cascade_focus_09_11_2025 → main
**Total Rules Implemented:** 27 rules across 6 stages
**Status:** ✅ Ready for Testing
