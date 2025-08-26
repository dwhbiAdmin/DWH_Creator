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
├── templates/             # DDL/ETL template files
├── tests/                 # Unit tests
├── config/                # Configuration files
├── _DWH_Projects/         # Default location for created projects
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

3. Run the application:
```bash
python main.py --help
```

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
