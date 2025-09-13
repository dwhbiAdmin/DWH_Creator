# Anchor Navigation Guidelines
## DWH Creator Project

This document outlines how to use and maintain anchor comments throughout the DWH Creator codebase for better navigation.

## 📍 What are Anchors?

Anchors are special comments that create navigation points in your code using the **Comment Anchors** VS Code extension. They appear in the Anchors panel for quick navigation.

## 🎯 Anchor Types Used

### Primary Anchors
- `ANCHOR:` - Main navigation points and logical sections
- `TODO:` - Tasks to be implemented
- `FIXME:` - Known issues that need fixing
- `NOTE:` - Important information and reminders
- `SECTION:` - Major code sections

## 📂 Current Anchor Structure

### Backend Files

#### `src/backend/project_manager.py`
- **Imports and Dependencies** - All import statements
- **ProjectManager Class Definition** - Class start
- **Initialization and Configuration** - Constructor and setup
- **Project Creation Methods** - New project creation logic
- **Excel Workbook Creation Methods** - Workbook setup
- **Project Management Methods** - Open/validate projects
- **Project Validation and Utility Methods** - Helper functions
- **Excel and External Integration Methods** - External tool integration
- **Git Integration Methods** - Version control features

#### `src/backend/workbench_manager.py`
- **Imports and Dependencies** - All import statements
- **WorkbenchManager Class Definition** - Class start
- **Initialization and Setup Methods** - Constructor and setup
- **Sheet Opening Methods** - Excel sheet operations
- **Import and CSV Processing Methods** - Data import logic
- **CSV Analysis Helper Methods** - CSV processing utilities
- **Workbook Data Management Methods** - Data manipulation
- **AI Comment Generation Methods** - Public AI methods
- **Private AI Generation Helper Methods** - Internal AI logic
- **Cascade and Sync Operations** - Future functionality
- **Workbook Management Methods** - Save/backup operations

### Frontend Files

#### `src/frontend/console_interface.py`
- **Imports and Dependencies** - All import statements
- **ConsoleInterface Class Definition** - Class start
- **Initialization and Setup** - Constructor and configuration
- **Display and Menu Methods** - UI display logic
- **Project Management Handlers** - Project operations
- **Status and Utility Methods** - Helper methods
- **Main Application Loop** - Core application flow
- **Workbench Operations Handler** - Workbench menu
- **Workbench Operation Helper Methods** - Individual operations
- **AI Comment Generation Handlers** - AI functionality
- **Additional Operations Handlers** - Misc operations
- **Main Application Entry Point** - Entry point

### Utility Files

#### `src/utils/excel_utils.py`
- **Imports and Dependencies** - All import statements
- **ExcelUtils Class Definition** - Class start
- **Workbook Creation Methods** - Workbook creation logic

#### `src/utils/ai_comment_generator.py`
- **Imports and Dependencies** - All import statements
- **AICommentGenerator Class Definition** - Class start
- **Initialization and Setup** - Constructor and API setup

#### `src/utils/config_manager.py`
- **ConfigManager Class Definition** - Class start
- **Default Configuration Constants** - Configuration data

#### `src/utils/logger.py`
- **Imports and Dependencies** - All import statements
- **Logger Class Definition** - Class start
- **Initialization and Setup** - Logger configuration
- **Logging Methods** - Logging functionality

## 🔧 How to Maintain Anchors

### When Adding New Methods
```python
# Add anchor before method groups
# ANCHOR: New Feature Methods
def new_feature_method(self):
    pass
```

### When Adding New Classes
```python
# ANCHOR: NewClass Definition
class NewClass:
    pass
```

### When Adding New Sections
```python
# ANCHOR: Data Processing Methods
def process_data(self):
    pass

def validate_data(self):
    pass
```

## 📋 Best Practices

### 1. Anchor Placement
- Place anchors **before** the code section they describe
- Use descriptive names that clearly indicate the section purpose
- Group related methods under the same anchor

### 2. Naming Conventions
- Use title case for anchor names: "Method Name Here"
- Be specific: "AI Comment Generation Methods" vs "AI Methods"
- Include the word "Methods" for method groups

### 3. Consistency
- Follow the established pattern in each file
- Keep similar anchor structures across similar files
- Update this document when adding new anchor categories

### 4. When to Add Anchors
- **Always** add anchors when creating new files
- Add anchors when adding new logical sections (3+ related methods)
- Add anchors for major refactoring or restructuring

### 5. When NOT to Add Anchors
- Don't add anchors for single methods unless they're entry points
- Avoid anchors for very short files (< 50 lines)
- Don't duplicate anchors within the same file

## 🔍 Using Anchors for Navigation

### View All Anchors
1. Press `Ctrl+Shift+P`
2. Type "Anchors: List All"
3. Click any anchor to jump to it

### Anchor Panel
- Look for the "Anchors" section in your Explorer sidebar
- Click any anchor to navigate
- Anchors are organized by file

### Keyboard Shortcuts
- `Ctrl+Shift+P` → "Anchors: Go to Anchor"
- Navigate using the command palette

## 🔄 Updating Guidelines

When you add new anchor patterns or restructure files:

1. Update this document with the new structure
2. Follow the established naming conventions
3. Consider the impact on team navigation
4. Test that anchors work correctly in VS Code

## 💡 Tips

- Use anchors to create a "table of contents" for your code
- Anchors are especially useful in large files (200+ lines)
- Consider the logical flow when placing anchors
- Review anchor organization during code reviews

---

**Remember**: Anchors are for navigation, not documentation. Keep them concise and focused on structure!
