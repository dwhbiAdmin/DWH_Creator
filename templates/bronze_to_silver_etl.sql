-- ETL Template for Bronze to Silver
-- Stage: 2_silver  
-- Purpose: Transform bronze data to silver layer with basic cleansing

INSERT INTO {target_database}.{target_schema}.{target_table}
(
    {list_comma_target_columns}
)
SELECT 
    {list_comma_source_mappings}
FROM {source_database}.{source_schema}.{source_table} src
WHERE src.batch_id = '{batch_id}'
  AND src.created_timestamp >= '{start_timestamp}'
  AND src.created_timestamp < '{end_timestamp}';
