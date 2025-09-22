# DWH Creator

A Data Warehouse Creator project for building and managing data warehouse solutions.

## Overview

This project aims to simplify the creation and management of data warehouse infrastructure through a metadata-driven approach. The tool generates DDL scripts, ETL pipelines, and documentation from Excel-based metadata definitions.

## Project Structure

```
DWH_Creator/
├── src/
│   ├── backend/           # Core business logic modules
│   │   ├── project_manager.py     # Project creation and management (Step 1)
│   │   ├── workbench_manager.py   # Excel workbook operations (Step 2) 
│   │   ├── template_engine.py     # Template processing (Step 3)
│   │   ├── artifact_generator.py  # Artifact generation (Step 4)
│   │   ├── list_generator.py      # List generation utilities (Helper A)
│   │   └── git_manager.py         # Git integration (Helper B)
│   ├── frontend/          # User interface components
│   ├── utils/             # Common utilities and helpers
│   │   ├── config_manager.py      # Configuration management
│   │   ├── logger.py              # Logging utilities
│   │   ├── A_file_utils.py        # File operations
│   │   ├── excel_utils.py         # Excel-specific utilities
│   │   ├── column_cascading.py    # Enhanced column cascading engine
│   │   └── relation_processor.py  # Deterministic relation processing logic
│   └── __init__.py
├── templates/             # Global DDL/ETL template files (shared across all projects)
├── tests/                 # Unit tests
├── config/                # Configuration files
├── _DWH_Projects/         # Default location for created projects
│   └── Project_<name>/    # Individual project structure:
│       ├── 1_sources/     # Source files for import
│       ├── 2_workbench/   # Excel workbook and metadata
│       ├── 4_artifacts/   # Generated DDL/ETL scripts
│       └── 9_archive/     # Archived versions
├── requirements.txt       # Python dependencies
├── main.py               # Application entry point
└── README.md
```

## Key Features

### ✅ Implemented Features

- **Metadata-Driven Design**: Define data warehouse structure in Excel workbooks
- **Project Management**: Create and manage multiple DWH projects with standardized structure
- **AI-Powered Business Column Names**: Generate business-friendly column names using OpenAI
- **Advanced Column Cascading**: Intelligent column propagation across data warehouse stages
  - **Enhanced Relation Processing**: Context-aware deterministic relation logic with artifact type detection
  - **Project-Specific Configurations**: Automatic creation of `cascading_config_{ProjectName}.xlsx`
  - **Globally Unique Column IDs**: Sequential unique identifiers (c1 to c108+)
  - **Hierarchical Column Ordering**: SK → BK → Attributes → Technical fields
  - **Stage-Aware Propagation**: Control column flow between stages (s0-s6)
  - **Multi-Relation Support**: Main, get_key, lookup, and PBI relation types
  - **Technical Field Injection**: Automatic stage and artifact-specific technical columns
- **Excel Integration**: Native Excel workbook operations with COM integration
- **Template-Based Generation**: Generate DDL and ETL scripts from customizable templates  

### 🚧 Planned Features

- **Multi-Stage Architecture**: Support for drop zone, bronze, silver, gold, mart, and BI layers
- **Git Integration**: Version control for projects and artifacts
- **Multiple UI Options**: Console, GUI, and future web interfaces
- **Advanced ETL Generation**: Complete ETL pipeline automation

## Getting Started

### Prerequisites

- Python 3.8+
- Git
- Excel (for workbook editing)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/dwhbiAdmin/DWH_Creator.git
cd DWH_Creator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure the application:
```bash
# Copy the configuration template
cp config/config.ini.template config/config.ini

# Edit config/config.ini and add your OpenAI API key:
# api_key = your_openai_api_key_here
```

4. Run the application:
```bash
python main.py --console
```

## Configuration

The application uses a configuration file `config/config.ini` for settings. 

### Setup Configuration

1. Copy the template: `cp config/config.ini.template config/config.ini`
2. Edit `config/config.ini` with your settings:

```ini
[openai]
# Your OpenAI API key for AI comment generation
api_key = your_openai_api_key_here
model = gpt-4

[application]
default_projects_folder = _DWH_Projects
log_level = INFO
```

### Environment Variables

You can also set configuration via environment variables:
- `OPENAI_API_KEY` - OpenAI API key (overrides config file)

### Security Note

⚠️ **Never commit `config/config.ini` to version control!** 
The file is automatically ignored by `.gitignore` to protect your API keys.

## Development Status

**Current Status**: ✅ **Production Ready Core Features**

### Completed Modules:
- ✅ **Project Management**: Full project creation and structure management
- ✅ **Workbench Operations**: Excel workbook creation and data management  
- ✅ **AI Integration**: Business column name generation with OpenAI
- ✅ **Column Cascading Engine**: Advanced column propagation with unique IDs
- ✅ **Configuration Management**: Project-specific and global configuration system

### Recent Enhancements (September 2025):
- 🆕 **Enhanced Relation Processing**: Deterministic context-aware relation logic with artifact type detection
  - Smart artifact type detection (dimension, fact, bridge) based on naming patterns and explicit types
  - Context-aware stage transition processing (s0→s1 through s5→s6)
  - Relation-specific processing: main, get_key, lookup, and PBI cascading patterns
  - Automatic technical field generation based on stage and artifact type
- 🆕 **Project-Specific Cascading Configs**: Auto-created `cascading_config_{ProjectName}.xlsx` files
- 🆕 **Globally Unique Column IDs**: Sequential ID generation (c1-c108+) 
- 🆕 **Hierarchical Column Ordering**: Automatic SK→BK→Attributes→Technical ordering
- 🆕 **Enhanced Stage Control**: Improved column flow control between data warehouse stages

### Next Development Phase:
- Template engine implementation
- DDL/ETL artifact generation
- Git integration features

## 📚 Documentation

Comprehensive documentation is available in the `/documentation` directory:

- **[📖 Documentation Index](documentation/index.md)** - Start here for complete documentation overview
- **[🚀 Quick Start](documentation/QUICK_START.md)** - Get up and running quickly
- **[📋 Release Notes](documentation/RELEASE_NOTES_SEPTEMBER_2025.md)** - Latest features and improvements

### Documentation Structure:
- **`user-guides/`** - Step-by-step user documentation
- **`technical/`** - Architecture and implementation details  
- **`reference/`** - Command references and patterns
- **`implementation/`** - Implementation summaries and status
- **`guidelines/`** - Development standards and guidelines
- **`specifications/`** - Original requirements and specifications

## Architecture

The application follows a modular architecture with clear separation between:

- **Backend**: Core business logic organized in numbered modules for logical flow
- **Frontend**: UI components supporting multiple interface types
- **Utils**: Common utilities and helper functions
- **Templates**: Reusable DDL/ETL template files

## Contributing

Please follow the contribution guidelines when making changes to this project.

## License

[Add license information here]
