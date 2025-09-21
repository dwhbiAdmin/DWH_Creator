# Workbook Templates

This directory contains the standard workbook templates for DWH Creator projects.

## Templates

### `workbench_template.xlsx`
- **Purpose**: Main project workbench template for new DWH projects
- **Source**: Based on corrected AdventureWorks project workbench
- **Last Updated**: September 21, 2025
- **Sheets**:
  - `Artifacts`: Project artifacts with IDs, names, types, and relationships
  - `Stages`: Data pipeline stages configuration
  - `Columns`: Column definitions with data types, comments, and business names

### `cascading_config_template.xlsx`
- **Purpose**: Column cascading configuration template
- **Source**: Enhanced configuration with RelationProcessor support
- **Last Updated**: September 21, 2025
- **Sheets**:
  - `DataTypeMappings`: Cross-platform data type mappings (28 types)
  - `TechnicalColumns`: Stage-specific technical column configurations (36 fields)
  - `StageConfiguration`: Pipeline stage definitions (7 stages)
  - `RelationTypes`: Relation processing documentation (4 types)

## Usage

When creating a new DWH project:

1. Copy `workbench_template.xlsx` to your project's `2_workbench` directory
2. Rename to `workbench_[ProjectName].xlsx`
3. Copy `cascading_config_template.xlsx` to your project's `2_workbench` directory  
4. Rename to `cascading_config_[ProjectName].xlsx`
5. Customize the templates with your project-specific data

## Features

- **Enhanced Relation Processing**: Support for context-aware relation processing
- **Stage ID Mappings**: Proper stage identification (s0-s6)
- **Artifact Type Support**: Dimension, Fact, and Bridge artifact types
- **Technical Field Management**: Comprehensive technical column configurations
- **Cross-Platform Support**: SQL Server, Databricks, and Power BI compatibility

## Version History

- **v1.0** (2025-09-21): Initial templates based on AdventureWorks project corrections
  - Added enhanced technical column configurations
  - Integrated RelationProcessor support
  - Added comprehensive data type mappings
  - Included stage and relation type documentation