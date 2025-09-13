# Getting Started with DWH Creator

## 📋 Table of Contents
- [Welcome](#welcome)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [First Steps](#first-steps)
- [Your First Project](#your-first-project)
- [Basic Workflows](#basic-workflows)
- [AI Features Walkthrough](#ai-features-walkthrough)
- [Next Steps](#next-steps)
- [Getting Help](#getting-help)

## 👋 Welcome

Welcome to **DWH Creator** - your comprehensive tool for building and managing data warehouses with AI-powered automation. This guide will help you get up and running quickly with your first project.

### What You'll Learn

- How to install and configure DWH Creator
- Create your first data warehouse project
- Use AI features to automate documentation
- Navigate the workbench operations
- Best practices for ongoing development

### Time Required
**Estimated: 30 minutes** for complete setup and first project creation

## ✅ Prerequisites

### System Requirements

- **Operating System**: Windows 10/11 (primary), macOS, Linux
- **Python**: Version 3.8 or higher
- **Microsoft Excel**: Required for workbook operations
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: 1GB free space for projects and dependencies

### Required Accounts

1. **OpenAI Account**: For AI-powered features
   - Sign up at [platform.openai.com](https://platform.openai.com)
   - Obtain API key with GPT-3.5 or GPT-4 access
   - Ensure account has sufficient credits

### Skills Assumed

- Basic command line usage
- Basic Excel knowledge
- Understanding of data warehouse concepts
- Familiarity with database terminology

## 🚀 Installation

### Step 1: Download DWH Creator

```bash
# Clone from GitHub
git clone https://github.com/dwhbiAdmin/DWH_Creator.git
cd DWH_Creator
```

### Step 2: Set Up Python Environment

```bash
# Check Python version
python --version  # Should be 3.8+

# Create virtual environment (recommended)
python -m venv dwh_creator_env

# Activate virtual environment
# Windows:
dwh_creator_env\Scripts\activate
# macOS/Linux:
source dwh_creator_env/bin/activate
```

### Step 3: Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt

# Verify installation
python -c "import pandas, openpyxl, openai; print('✅ All dependencies installed')"
```

### Step 4: Configure OpenAI API

1. **Create configuration file:**
   ```bash
   # Copy template
   copy config\config.ini.template config\config.ini
   ```

2. **Edit configuration file:**
   ```ini
   # config/config.ini
   [openai]
   api_key = your_openai_api_key_here
   model = gpt-3.5-turbo
   temperature = 0.3
   max_tokens = 50
   ```

3. **Test configuration:**
   ```bash
   # Verify API connection
   python -c "
   from src.utils.ai_comment_generator import AICommentGenerator
   ai = AICommentGenerator('your_api_key_here')
   print('✅ OpenAI connection successful' if ai.is_available() else '❌ Connection failed')
   "
   ```

### Step 5: Verify Installation

```bash
# Test basic functionality
python main.py --console

# You should see:
# 🏗️  DWH Creator - Data Warehouse Creation Tool
# ==================================================
# Starting in console mode...
```

## 🏁 First Steps

### Launch DWH Creator

```bash
# Start the application
python main.py --console
```

You'll see the main menu:

```
============================================================
🏗️  DWH Creator - Data Warehouse Creation Tool
   Console Interface v1.0
============================================================

❌ No project currently open

📋 Main Menu:
1. Create New Project
2. Open Existing Project
0. Exit
----------------------------------------
```

### Understanding the Interface

- **Menu Navigation**: Use numbers to select options
- **Back Navigation**: Option 0 usually returns to previous menu
- **Status Display**: Shows current project and location
- **Progress Feedback**: Real-time updates during operations

## 🎯 Your First Project

### Step 1: Create New Project

1. **Select option 1** from main menu
2. **Enter project name**: `MyFirstDWH`
3. **Choose location**: Press Enter for default or specify custom path

```bash
🆕 Create New Project
------------------------------
Enter project name: MyFirstDWH
Default location: C:\Users\[user]\repos\DWH_Creator\_DWH_Projects
Enter custom path (or press Enter for default): [Enter]

🔨 Creating project 'MyFirstDWH'...
✅ Project created successfully!
📁 Project location: C:\Users\[user]\repos\DWH_Creator\_DWH_Projects\Project_MyFirstDWH
```

### Step 2: Explore Project Structure

Your project now has this structure:

```
Project_MyFirstDWH/
├── 1_sources/              # Source data files
├── 2_workbench/           # Main Excel workbook
│   └── workbench_MyFirstDWH.xlsx
├── 3_target/              # Output artifacts
├── 4_documentation/       # Project documentation
└── 5_scripts/            # SQL and other scripts
```

### Step 3: Open Excel Workbook

When prompted:
```bash
⚠️  Note: If you open the Excel workbook, you'll need to close it before import operations
📊 Open Excel workbook now? (y/n): y
```

**Choose 'y'** to open and explore the workbook structure:
- **Stages**: Define data processing stages
- **Artifacts**: Define data objects (tables, views)
- **Columns**: Define column structures and metadata

## 🔄 Basic Workflows

### Workflow 1: Import Source Data

1. **Navigate to Workbench Operations** (option 3)
2. **Select Import/Assign from 1_sources** (option 4)

```bash
🔧 Workbench Operations
------------------------------
4. Import/Assign from 1_sources ← Select this
```

This will scan your `1_sources` folder and import available data files.

### Workflow 2: Define Stages

1. **Open Stages Sheet** (option 1)
2. Review the default stages:
   - `0_drop_zone`: Raw data landing
   - `1_bronze`: Cleaned and validated data
   - `2_silver`: Business rules applied
   - `3_gold`: Analytics-ready data

### Workflow 3: Add Sample Data

Create a sample CSV file to practice with:

1. **Create sample file** in `1_sources/` folder:
   ```csv
   # customer.csv
   cust_ID,cust_Name,cust_Email
   1001,John Smith,john.smith@email.com
   1002,Jane Doe,jane.doe@email.com
   1003,Bob Johnson,bob.johnson@email.com
   ```

2. **Import the file** using option 4 in Workbench Operations

## 🤖 AI Features Walkthrough

### Feature 1: Generate Artifact Comments

**Purpose**: Create business descriptions for your data artifacts

1. **Navigate to Workbench Operations** → **Generate AI Comments (Artifacts)** (option 5)
2. **Confirm generation**: Type 'y' when prompted
3. **Review results**: Check the Artifacts sheet for generated comments

**Example Result**:
```
Artifact: customer.csv
Generated Comment: "Customer master data containing unique customer identifiers, names, and contact information for business operations and analytics."
```

### Feature 2: Generate Column Comments

**Purpose**: Create detailed explanations for database columns

1. **Select Generate AI Comments (Columns)** (option 6)
2. **Confirm generation**: Type 'y' when prompted
3. **Review results**: Check the Columns sheet for generated comments

**Example Results**:
```
Column: cust_ID
Generated Comment: "Unique identifier for each customer in the system"

Column: cust_Name  
Generated Comment: "Customer's full name as provided during registration"

Column: cust_Email
Generated Comment: "Primary email address for customer communication"
```

### Feature 3: Generate Readable Column Names

**Purpose**: Convert technical names to business-friendly snake_case format

1. **Select Generate Readable Column Names** (option 7)
2. **Confirm generation**: Type 'y' when prompted
3. **Review results**: Check the new "Readable Column Name" column

**Example Results**:
```
Technical Name    → Readable Name
cust_ID          → customer_id
cust_Name        → customer_name  
cust_Email       → customer_email
```

### Understanding AI Progress

During AI operations, you'll see detailed progress:

```bash
⏳ Generating readable column names...
2025-09-13 19:54:45 - DWH_Creator - INFO - Generating readable names for 3 columns...
2025-09-13 19:54:46 - DWH_Creator - INFO - Generated readable name for cust_ID: customer_id
2025-09-13 19:54:47 - DWH_Creator - INFO - Generated readable name for cust_Name: customer_name
2025-09-13 19:54:48 - DWH_Creator - INFO - Generated readable name for cust_Email: customer_email
✅ Readable column names generated successfully!
```

## 📊 Working with Results

### Viewing AI-Generated Content

1. **Open the Excel workbook** (close and reopen if needed)
2. **Navigate between sheets**:
   - **Artifacts sheet**: Review artifact comments
   - **Columns sheet**: Review column comments and readable names

### Customizing Generated Content

1. **Manual Editing**: Edit any AI-generated content directly in Excel
2. **Regeneration**: Run AI features again to update content
3. **Selective Updates**: AI only updates empty fields, preserving manual edits

### Saving Your Work

1. **Use Save Workbook** (option 10) in Workbench Operations
2. **Or use Excel's save function** (Ctrl+S)

## 🎯 Next Steps

### Expand Your Project

1. **Add More Source Files**: 
   - Create additional CSV files in `1_sources/`
   - Import and process them through the workbench

2. **Define Business Rules**:
   - Add validation rules in the Columns sheet
   - Define transformation logic

3. **Create Target Artifacts**:
   - Define views and tables for each stage
   - Use readable column names for gold layer

### Advanced Features

1. **Cascade Operations**: Propagate changes across stages
2. **Data Validation**: Use AI for quality checks
3. **Documentation Generation**: Create comprehensive project docs

### Learn More

1. **Read User Guides**:
   - [Workbench Operations](workbench-operations.md)
   - [AI Features](ai-comments.md)
   - [Data Integration](data-integration.md)

2. **Explore Technical Docs**:
   - [System Architecture](../technical/architecture.md)
   - [AI Integration](../technical/ai-integration.md)

## 🆘 Getting Help

### Common First-Time Issues

#### Issue: "AI comment generation not available"
**Solution**: 
1. Check your OpenAI API key in `config/config.ini`
2. Verify internet connection
3. Ensure API key has sufficient credits

#### Issue: "Excel file appears to be open"
**Solution**:
1. Close Excel completely
2. Check Task Manager for hidden Excel processes
3. Restart the operation

#### Issue: "No data found to import"
**Solution**:
1. Add CSV files to the `1_sources/` folder
2. Ensure files have proper headers
3. Use supported file formats (CSV, Excel)

### Getting Support

1. **Documentation**: Check the complete documentation in `/documentation/`
2. **Issues**: Report problems on GitHub Issues
3. **Community**: Join discussions on GitHub Discussions

### Best Practices for Beginners

1. **Start Small**: Begin with simple CSV files
2. **Regular Saves**: Save your work frequently
3. **Backup Projects**: Keep copies of important projects
4. **Experiment Safely**: Test AI features on sample data first
5. **Review Results**: Always review AI-generated content for accuracy

## 🎉 Congratulations!

You've successfully:
- ✅ Installed and configured DWH Creator
- ✅ Created your first project
- ✅ Used AI features to generate business content
- ✅ Learned basic workflows and navigation

You're now ready to start building production data warehouses with DWH Creator!

### What's Next?

1. **Create a real project** with your actual data sources
2. **Explore advanced AI features** for complex scenarios
3. **Learn about data integration** and business rule implementation
4. **Join the community** to share experiences and get help

---

## 📚 Quick Reference

### Essential Commands
```bash
# Start DWH Creator
python main.py --console

# Create new project
Main Menu → 1. Create New Project

# AI Features
Workbench Operations → 5. Generate AI Comments (Artifacts)
Workbench Operations → 6. Generate AI Comments (Columns)  
Workbench Operations → 7. Generate Readable Column Names

# Save work
Workbench Operations → 10. Save Workbook
```

### Key File Locations
- **Configuration**: `config/config.ini`
- **Projects**: `_DWH_Projects/Project_[name]/`
- **Documentation**: `documentation/`
- **Logs**: Check console output for detailed logging

---

*Welcome to the DWH Creator community! Happy data warehousing! 🚀*

*Last updated: September 13, 2025*
