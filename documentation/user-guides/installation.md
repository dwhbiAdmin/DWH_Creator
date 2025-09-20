# Installation Guide for DWH Creator

## 📋 Table of Contents
- [System Requirements](#system-requirements)
- [Pre-Installation Checklist](#pre-installation-checklist)
- [Installation Methods](#installation-methods)
- [Configuration Setup](#configuration-setup)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)
- [Next Steps](#next-steps)

## 🖥️ System Requirements

### Operating System Support
| OS | Version | Status | Notes |
|---|---|---|---|
| **Windows** | 10/11 | ✅ Primary | Fully tested and supported |
| **macOS** | 10.15+ | ✅ Supported | Tested on Intel and Apple Silicon |
| **Linux** | Ubuntu 18.04+ | ✅ Supported | Debian-based distributions |

### Hardware Requirements
- **CPU**: 2+ cores (4+ recommended for AI features)
- **RAM**: 4GB minimum (8GB+ recommended)
- **Storage**: 2GB free space for installation and projects
- **Network**: Internet connection for AI features and package installation

### Software Dependencies
- **Python**: 3.8, 3.9, 3.10, or 3.11 (3.12 not yet tested)
- **Microsoft Excel**: 2016 or newer (for workbook operations)
- **Git**: Latest version (for cloning repository)

## ✅ Pre-Installation Checklist

### 1. Python Installation Verification
```bash
# Check Python version
python --version
# Should show Python 3.8.x or higher

# Check pip installation
pip --version
# Should show pip version
```

### 2. Excel Availability
- Ensure Microsoft Excel is installed and licensed
- Test that you can create and edit `.xlsx` files
- Verify Excel can handle workbooks with multiple sheets

### 3. OpenAI API Setup (Optional but Recommended)
1. **Create OpenAI Account**
   - Visit [platform.openai.com](https://platform.openai.com)
   - Sign up for an account
   - Add payment method (required for API usage)

2. **Generate API Key**
   - Navigate to API Keys section
   - Create new secret key
   - **Important**: Copy and securely store the key immediately
   - Set usage limits to control costs

3. **Verify API Access**
   ```bash
   # Test API access (optional)
   curl -H "Authorization: Bearer YOUR_API_KEY" \
        https://api.openai.com/v1/models
   ```

## 🔧 Installation Methods

### Method 1: Git Clone (Recommended)

1. **Clone Repository**
   ```bash
   # Clone the repository
   git clone https://github.com/your-org/DWH_Creator.git
   cd DWH_Creator
   ```

2. **Create Virtual Environment**
   ```bash
   # Windows
   python -m venv dwh_env
   dwh_env\Scripts\activate

   # macOS/Linux
   python -m venv dwh_env
   source dwh_env/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   # Install required packages
   pip install -r requirements.txt
   ```

### Method 2: Download ZIP

1. **Download Source**
   - Visit the repository page
   - Click "Code" → "Download ZIP"
   - Extract to desired location

2. **Follow steps 2-3** from Method 1

### Method 3: Development Installation

1. **Clone with Development Dependencies**
   ```bash
   git clone https://github.com/your-org/DWH_Creator.git
   cd DWH_Creator
   
   # Install in development mode
   pip install -e .
   pip install -r requirements-dev.txt
   ```

## ⚙️ Configuration Setup

### 1. Environment Configuration

Create a `.env` file in the project root:
```bash
# Copy template
cp .env.template .env
```

Edit `.env` with your settings:
```env
# OpenAI Configuration
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-3.5-turbo

# Project Settings
DEFAULT_PROJECT_PATH=./projects
LOG_LEVEL=INFO

# Excel Settings
EXCEL_BACKUP_ENABLED=true
EXCEL_AUTO_SAVE=true
```

### 2. Directory Structure Setup

The installer will create this structure:
```
DWH_Creator/
├── projects/               # Your project workspaces
├── templates/             # Excel templates
├── logs/                  # Application logs
├── config/               # Configuration files
└── backups/              # Automatic backups
```

### 3. Application Configuration

Run the configuration wizard:
```bash
python -m src.setup.configure
```

This will:
- Test Python dependencies
- Verify Excel integration
- Test OpenAI API connection
- Create default project structure
- Generate sample project

## ✅ Verification

### 1. Basic Installation Test
```bash
# Test core functionality
python -m src.main --version

# Expected output:
# DWH Creator v1.0.0
```

### 2. Module Import Test
```bash
python -c "
from src.utils.config_manager import ConfigManager
from src.utils.excel_utils import ExcelUtils
print('✅ Core modules imported successfully')
"
```

### 3. Excel Integration Test
```bash
# Run Excel test
python -m src.tests.verify_excel
```

### 4. AI Features Test (if API key configured)
```bash
# Test AI integration
python -m src.tests.verify_ai
```

### 5. Complete System Test
```bash
# Run full verification
python -m src.tests.verify_installation
```

## 🔧 Troubleshooting

### Common Issues

#### "Module not found" Errors
```bash
# Ensure virtual environment is activated
# Windows
dwh_env\Scripts\activate

# macOS/Linux  
source dwh_env/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

#### Excel Permission Issues
- **Windows**: Run as Administrator if needed
- **macOS**: Grant Excel permissions in System Preferences
- **Linux**: Ensure LibreOffice is installed as fallback

#### OpenAI API Errors
```bash
# Test API key format
python -c "
import os
key = os.getenv('OPENAI_API_KEY')
if key and key.startswith('sk-'):
    print('✅ API key format looks correct')
else:
    print('❌ API key missing or invalid format')
"
```

#### Python Version Issues
```bash
# Check Python version compatibility
python -c "
import sys
version = sys.version_info
if version >= (3, 8):
    print(f'✅ Python {version.major}.{version.minor} is compatible')
else:
    print(f'❌ Python {version.major}.{version.minor} is too old, need 3.8+')
"
```

### Advanced Troubleshooting

#### Dependency Conflicts
```bash
# Create fresh environment
rm -rf dwh_env
python -m venv dwh_env --clear
source dwh_env/bin/activate  # or dwh_env\Scripts\activate on Windows
pip install --upgrade pip
pip install -r requirements.txt
```

#### Excel/Openpyxl Issues
```bash
# Test Excel functionality
python -c "
import openpyxl
import pandas as pd
wb = openpyxl.Workbook()
print('✅ Excel operations working')
"
```

#### Memory Issues
- Increase system RAM or use swap space
- Process large workbooks in chunks
- Enable memory optimization in configuration

## 🎯 Next Steps

### Immediate Next Steps
1. **[Follow Getting Started Guide](getting-started.md)** - Create your first project
2. **[Learn AI Features](business-column-names.md)** - Use AI-powered automation
3. **[Review User Workflows](user-workflows.md)** - Master the complete process

### Recommended Learning Path
1. ✅ **Installation** (this guide)
2. 🎯 **Basic Usage** - Create sample project
3. 🤖 **AI Features** - Generate comments and names
4. 📊 **Advanced Workflows** - Complex data warehouse projects
5. 🔧 **Customization** - Adapt to your organization's needs

### Getting Help

#### Documentation Resources
- [User Guides](../user-guides/) - Step-by-step instructions
- [Technical Documentation](../technical/) - Architecture and APIs
- [Specifications](../specifications/) - Requirements and design

#### Support Channels
- **GitHub Issues**: Bug reports and feature requests
- **Documentation**: Comprehensive guides and examples
- **Community**: User forums and discussions

#### Emergency Contacts
- **Critical Issues**: Create GitHub issue with "urgent" label
- **Security Issues**: Email security@yourcompany.com
- **Installation Problems**: Check troubleshooting section above

---

## 📝 Installation Summary

After successful installation, you should have:
- ✅ DWH Creator installed and configured
- ✅ Python environment with all dependencies
- ✅ Excel integration working
- ✅ OpenAI API configured (optional)
- ✅ Project directory structure created
- ✅ Sample project available for testing

**Total Installation Time**: 15-30 minutes depending on internet speed and system performance.

Ready to create your first data warehouse project? **[Continue to Getting Started Guide →](getting-started.md)**
