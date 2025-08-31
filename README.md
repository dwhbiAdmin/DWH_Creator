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
│   │   ├── file_utils.py          # File operations
│   │   └── excel_utils.py         # Excel-specific utilities
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

## Key Features (Planned)

- **Metadata-Driven Design**: Define data warehouse structure in Excel workbooks
- **Template-Based Generation**: Generate DDL and ETL scripts from customizable templates  
- **Multi-Stage Architecture**: Support for drop zone, bronze, silver, gold, mart, and BI layers
- **Git Integration**: Version control for projects and artifacts
- **Modular Backend**: Clean separation of concerns with step-by-step processing
- **Multiple UI Options**: Console, GUI, and future web interfaces

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

This project is currently in the skeleton creation phase. Implementation will proceed step-by-step under guided development.

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
