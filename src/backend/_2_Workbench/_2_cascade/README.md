# Cascade Rules Module

This module contains stage-specific cascade rules implementation based on the **CASCADE_and_OTHER_RULES.xlsx** file.

## Structure

Each stage has its own Python file implementing the cascading rules for that stage:

### Files Created

1. **s0_drop_zone_rules.py** - Drop Zone (s0) stage
   - `rule_drp_1`: AI estimate data types and business names
   - `rule_drp_2`: AI estimate primary keys

2. **s1_bronze_rules.py** - Bronze (s1) stage
   - `rule_brz_1`: Field selection (take all from s0)
   - `rule_brz_2`: Naming (preserve source names)
   - `rule_brz_3`: Source columns (source_column_name = column_name)
   - `rule_brz_4`: Data types (all STRING except technical/partition)
   - `rule_brz_5`: Order (preserve, start from 1)
   - `rule_brz_6`: Business names (AI estimation)
   - `rule_brz_7`: Technical fields (add bronze technical fields)
   - `rule_brz_8`: Other fields (set transformation fields, copy from s0)

3. **s2_silver_rules.py** - Silver (s2) stage
   - `rule_slv_1`: Field selection (all from s1 except partitions)
   - `rule_slv_2`: Table primary keys (add _PK fields from s0 PKs)
   - `rule_slv_3`: Technical fields (add silver technical fields)
   - `rule_slv_4`: Naming (use source names)
   - `rule_slv_5`: Data types (from s0, with platform conversion)
   - `rule_slv_6`: Source columns (source_column_name = column_name)
   - `rule_slv_7`: Other fields (copy from s0, handle PK sources)

4. **s3_gold_rules.py** - Gold (s3) stage
   - `rule_gld_1`: Field selection (from s2 main relation, no technical/partition)
   - `rule_gld_2`: Dimension SK (add surrogate key for dimensions)
   - `rule_gld_3`: Facts SKs (add SKs for get_key relations)
   - `rule_gld_4`: Dimension BK (add business key for dimensions)
   - `rule_gld_5`: Facts BKs (add BKs for get_key relations)
   - `rule_gld_6`: Technical fields (add gold technical field)
   - `rule_gld_7`: Naming (use business names if available)
   - `rule_gld_8`: Data types (from s2)
   - `rule_gld_9`: Source columns (from s2)

5. **s4_mart_rules.py** - Mart (s4) stage
   - `rule_mrt_1`: Field selection (take all from s3)

6. **s5_powerbi_model_rules.py** - PowerBI Model (s5) stage
   - Placeholder (no rules defined yet in Excel)

## Column Positions

The new transformation fields are now in columns **L-P**:
- **Column L**: `source_column_name`
- **Column M**: `lookup_fields`
- **Column N**: `etl_simple_trnasformation`
- **Column O**: `ai_transformation_prompt`
- **Column P**: `etl_ai_transformation`

## Usage

```python
from backend._2_Workbench._2_cascade import S1BronzeRules

# Initialize rules for bronze stage
bronze_rules = S1BronzeRules()

# Apply specific rule
new_columns = bronze_rules.rule_brz_1_field_selection(
    upstream_columns_df=s0_columns,
    target_columns_df=s1_columns,
    artifact_id='artifact_123'
)
```

## Implementation Notes

- Each rule is implemented as a separate function/method
- Rules are organized in the same order as in the CASCADE_and_OTHER_RULES.xlsx file
- Function names follow the pattern: `rule_{stage}_{number}_{description}`
- Each function includes complete documentation from the Excel file
- Simple, clear, and consistent implementation across all stages
- No extra functionality added beyond the rules specification
