-- DDL Template for Bronze Tables
-- Stage: 1_bronze
-- Purpose: Create bronze layer tables for raw data ingestion

CREATE OR REPLACE TABLE {database_name}.{schema_name}.{table_name} (
    {list_comma_column_datatype}
    , created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
    , source_system STRING
    , batch_id STRING
) 
USING DELTA
LOCATION '{table_location}'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);
