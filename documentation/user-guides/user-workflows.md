# User Workflows Guide

## 📋 Table of Contents
- [Overview](#overview)
- [Complete Workflow Walkthrough](#complete-workflow-walkthrough)
- [Column Cascading Workflows](#column-cascading-workflows)
- [Workflow Scenarios](#workflow-scenarios)
- [Advanced Workflows](#advanced-workflows)
- [Best Practices](#best-practices)
- [Troubleshooting Workflows](#troubleshooting-workflows)

## 🎯 Overview

This guide provides complete step-by-step workflows for using DWH Creator in real-world scenarios. Each workflow includes expected inputs, outputs, and decision points to help you successfully complete your data warehouse projects.

### Workflow Types Covered
- **🆕 New Project Setup** - From scratch to first working project
- **📊 Data Modeling** - Define stages, artifacts, and columns
- **🤖 AI Enhancement** - Use AI features for automation
- **🔧 Iterative Development** - Refine and improve projects
- **🚀 Production Deployment** - Prepare for production use

---

## 🚀 Complete Workflow Walkthrough

### Scenario: Creating a Sales Data Warehouse

**Context**: You need to create a data warehouse for sales analytics with bronze, silver, and gold layers.

**Time Required**: 45-60 minutes  
**Prerequisites**: DWH Creator installed, sample data available

#### Phase 1: Project Initialization (10 minutes)

1. **Launch DWH Creator**
   ```bash
   cd DWH_Creator
   python -m src.main
   ```

2. **Create New Project**
   - Select: `1. Create New Project`
   - Enter project name: `sales_analytics_dwh`
   - Choose location: `./projects/sales_analytics_dwh`
   - System creates project structure and workbook

3. **Verify Project Structure**
   ```
   projects/sales_analytics_dwh/
   ├── data/
   │   └── sales_analytics_dwh.xlsx
   ├── logs/
   ├── outputs/
   └── README.md
   ```

#### Phase 2: Define Data Stages (5 minutes)

1. **Access Workbook Management**
   - Select: `2. Open Existing Project`
   - Choose: `sales_analytics_dwh`
   - Select: `3. Manage Workbook`

2. **Add Stages**
   Open Excel workbook → Stages sheet:
   
   | Stage ID | Stage Name | Stage Description | Platform | Source/Business Side |
   |----------|------------|-------------------|----------|---------------------|
   | 1 | bronze | Raw data ingestion layer | Databricks | Source |
   | 2 | silver | Cleaned and validated data | Databricks | Source |
   | 3 | gold | Business-ready aggregated data | Databricks | Business |
   | 4 | mart | Department-specific views | Databricks | Business |

#### Phase 3: Define Artifacts (15 minutes)

1. **Navigate to Artifacts Sheet**
   
2. **Add Bronze Layer Artifacts**
   | Artifact ID | Artifact Name | Stage Name | Artifact Comment |
   |-------------|---------------|------------|------------------|
   | 1 | customers_bronze | bronze | Raw customer data from CRM system |
   | 2 | orders_bronze | bronze | Raw order transactions from e-commerce |
   | 3 | products_bronze | bronze | Raw product catalog from inventory system |

3. **Add Silver Layer Artifacts**
   | Artifact ID | Artifact Name | Stage Name | Artifact Comment |
   |-------------|---------------|------------|------------------|
   | 4 | customers_silver | silver | Cleaned customer data with validation |
   | 5 | orders_silver | silver | Validated order data with business rules |
   | 6 | products_silver | silver | Standardized product information |

4. **Add Gold Layer Artifacts**
   | Artifact ID | Artifact Name | Stage Name | Artifact Comment |
   |-------------|---------------|------------|------------------|
   | 7 | customer_metrics_gold | gold | Customer analytics and segmentation |
   | 8 | sales_summary_gold | gold | Aggregated sales performance metrics |
   | 9 | product_performance_gold | gold | Product sales and profitability analysis |

#### Phase 4: Define Columns (10 minutes)

1. **Add Key Columns for customers_bronze**
   | Column ID | Column Name | Artifact ID | Data Type | Column Business Name | Column Comment |
   |-----------|-------------|-------------|-----------|---------------------|----------------|
   | 1 | customer_id | 1 | INT | customer_id | Customer unique identifier |
   | 2 | first_name | 1 | VARCHAR(50) | customer_first_name | Customer first name |
   | 3 | last_name | 1 | VARCHAR(50) | customer_last_name | Customer last name |
   | 4 | email | 1 | VARCHAR(100) | customer_email | Customer email address |
   | 5 | created_timestamp | 1 | TIMESTAMP | record_created_timestamp | Record creation timestamp |

2. **Continue for Other Artifacts**
   - Add columns for orders_bronze (order_id, customer_id, order_date, total_amount, etc.)
   - Add columns for products_bronze (product_id, product_name, category, price, etc.)
   - Define derived columns for silver and gold layers

#### Phase 5: AI Enhancement (10 minutes)

1. **Generate AI Comments for Artifacts**
   - Return to main menu
   - Select: `5. Generate AI Comments (Artifacts)`
   - Confirm: `y` to proceed
   - AI generates business descriptions for all artifacts

2. **Generate AI Comments for Columns**
   - Select: `6. Generate AI Comments (Columns)`
   - Confirm: `y` to proceed
   - AI analyzes column names and generates explanations

3. **Generate Business Column Names**
   - Select: `7. Generate Business Column Names`
   - Confirm: `y` to proceed
   - AI creates business-friendly names for technical columns

#### Phase 6: Review and Refinement (5 minutes)

1. **Validate Data Model**
   - Review Stages sheet for completeness
   - Check Artifacts sheet for logical flow
   - Verify Columns sheet for data consistency

2. **Manual Refinements**
   - Edit AI-generated comments if needed
   - Adjust business column names for organizational standards
   - Add any missing artifacts or columns

3. **Save and Export**
   - Save Excel workbook
   - Export configurations if needed

---

## 🔄 Column Cascading Workflows

### What is Column Cascading?

Column cascading is an advanced feature that automatically propagates columns between data warehouse stages based on upstream relationships. This eliminates manual column definition and ensures consistency across your data pipeline.

#### Upstream Relationship Types

- **`main`** - Full column propagation with technical fields
- **`get_key`** - Dimension key propagation for fact tables  
- **`lookup`** - Limited column lookup (first 3 fields)
- **`pbi`** - No cascading impact (Power BI specific)

### Workflow: Setting Up Column Cascading

#### Prerequisites (5 minutes)

1. **Define Upstream Relationships**
   - Open workbook → Artifacts sheet
   - Set `Upstream Relation` field for each artifact:
     ```
     Bronze → Silver: "main"
     Silver → Gold (facts): "get_key" 
     Silver → Gold (lookups): "lookup"
     Gold → Power BI: "pbi"
     ```

2. **Configure Upstream Artifacts**
   - Set `Upstream Artifact` field with artifact IDs
   - Multiple artifacts: use comma separation (e.g., "1,2,3")

#### Phase 1: Configuration Setup (10 minutes)

1. **Create Cascading Configuration**
   - Go to: `Workbench Operations` → `Cascade Operations`
   - Select: `4. Create Cascading Configuration`
   - System creates `cascading_config.xlsx` with:
     - Data type mappings (SQL Server ↔ Databricks ↔ Power BI)
     - Technical columns per stage
     - Default cascading rules

2. **Customize Data Type Mappings** (Optional)
   - Open `cascading_config.xlsx`
   - Edit `DataTypeMappings` sheet for platform-specific types
   - Save changes

3. **Configure Technical Columns** (Optional)  
   - Edit `TechnicalColumns` sheet
   - Customize stage-specific technical fields
   - Mark optional columns as needed

#### Phase 2: Preview and Validate (5 minutes)

1. **Preview Cascading Impact**
   - Select: `3. Preview Cascading`
   - Review what columns will be created
   - Verify upstream relationships are correct

2. **List Upstream Artifacts**
   - Select: `5. List Artifacts with Upstream Relations`
   - Confirm all relationships are properly defined
   - Note any missing upstream connections

#### Phase 3: Execute Cascading (10 minutes)

1. **Cascade All Artifacts**
   - Select: `1. Cascade All Artifacts`
   - System processes all artifacts with upstream relationships
   - Monitor progress and success/failure counts

   **OR**

2. **Cascade Specific Artifact**
   - Select: `2. Cascade Specific Artifact`
   - Choose individual artifact for focused cascading
   - Useful for testing or incremental updates

3. **Verify Results**
   - Open Columns sheet in Excel
   - Check for new columns marked as `Cascaded: True`
   - Verify data types match target platform
   - Confirm technical columns are present

### Cascading Logic Examples

#### Example 1: Main Relationship (Bronze → Silver)

**Source (Bronze)**: `sales_data`
- sale_id (INT)
- customer_id (INT) 
- sale_date (DATETIME)
- amount (DECIMAL)

**Target (Silver)**: `clean_sales` with `Upstream Relation: main`

**Cascaded Result**:
```
# Business Columns (from source)
sale_id → sale_id (INT → BIGINT for Databricks)
customer_id → customer_id (INT → BIGINT)  
sale_date → sale_date (DATETIME → TIMESTAMP)
amount → amount (DECIMAL → DECIMAL)

# CDC Column
__bronze_last_changed_DT (TIMESTAMP)

# Technical Columns (Silver stage)
__silver_lastChanged_DT (TIMESTAMP) 
__silverPartition_xxxYear (INT)
__silverPartition_xxxMonth (INT)
__silverPartition_xxxDate (INT)
```

#### Example 2: Get_Key Relationship (Silver → Gold Fact)

**Sources**: 
- `clean_sales` (Silver fact data)
- `dim_customer` (Silver dimension)

**Target (Gold)**: `fact_sales` with `Upstream Relation: get_key`

**Cascaded Result**:
```
# Dimension Keys (ordinals 1-20)
dim_customer_SK (BIGINT) - Order: 1
dim_customer_BK (BIGINT) - Order: 21

# First 3 fields from upstream
sale_id (BIGINT)
customer_id (BIGINT) 
sale_date (TIMESTAMP)

# Technical Columns (Gold stage)
__gold_lastChanged_DT (TIMESTAMP)
__goldPartition_XXXYear (INT)
__goldPartition_XXXMonth (INT)
__goldPartition_XXXDate (INT)
```

### Platform-Specific Data Type Mapping

| SQL Server | Databricks | Power BI | Notes |
|------------|------------|----------|-------|
| INT | BIGINT | Whole Number | Integer promotion |
| VARCHAR | STRING | Text | String standardization |
| DATETIME | TIMESTAMP | Date/Time | Timestamp normalization |
| DECIMAL | DECIMAL | Decimal Number | Precision maintained |
| BIT | BOOLEAN | True/False | Boolean mapping |

### Best Practices for Column Cascading

#### 🎯 Planning Phase
- Define clear upstream relationships before cascading
- Use consistent naming conventions across stages
- Plan for platform-specific data type requirements

#### ⚙️ Configuration Phase  
- Customize technical columns for your organization
- Review default data type mappings
- Test cascading on small artifacts first

#### 🔍 Execution Phase
- Always preview before full cascading
- Cascade incrementally during development
- Validate results after each cascading operation

#### 🚀 Production Phase
- Document cascading rules for team
- Version control cascading configuration
- Monitor cascaded column consistency

### Troubleshooting Column Cascading

#### Common Issues

**No Columns Cascaded**
- ✅ Check `Upstream Relation` field is set
- ✅ Verify `Upstream Artifact` IDs exist
- ✅ Confirm source artifacts have columns

**Wrong Data Types**
- ✅ Review data type mapping configuration
- ✅ Check source platform vs target platform
- ✅ Verify custom mappings in config file

**Missing Technical Columns**  
- ✅ Check technical columns configuration
- ✅ Verify stage names match configuration
- ✅ Confirm optional vs required column settings

**Performance Issues**
- ✅ Cascade specific artifacts instead of all
- ✅ Break large operations into smaller chunks
- ✅ Check for circular relationship dependencies

---

## 🎪 Workflow Scenarios

### Scenario A: Migrating Existing Data Warehouse

**Context**: You have an existing data warehouse and want to document it in DWH Creator.

**Steps**:
1. **Inventory Existing Assets**
   - List all databases, schemas, tables
   - Document current data flow
   - Identify business stakeholders

2. **Create Project Structure**
   - Map existing layers to DWH Creator stages
   - Import table schemas as artifacts
   - Convert column metadata to DWH Creator format

3. **Use AI for Documentation**
   - Generate missing table descriptions
   - Create business-friendly column names
   - Fill documentation gaps with AI assistance

### Scenario B: Collaborative Team Development

**Context**: Multiple team members working on the same data warehouse project.

**Steps**:
1. **Setup Shared Project**
   - Create project in shared location (network drive/cloud)
   - Establish naming conventions
   - Define review processes

2. **Divide Responsibilities**
   - Assign stages to different team members
   - Use artifact ownership for tracking
   - Coordinate column definitions

3. **Regular Synchronization**
   - Schedule review meetings
   - Use Excel change tracking
   - Validate cross-dependencies

### Scenario C: Incremental Development

**Context**: Building data warehouse in phases over time.

**Steps**:
1. **Phase Planning**
   - Define MVP scope (minimum viable product)
   - Plan subsequent phases
   - Design for extensibility

2. **Iterative Implementation**
   - Start with core business entities
   - Add layers incrementally
   - Expand column definitions over time

3. **Version Management**
   - Save workbook versions at milestones
   - Document changes between versions
   - Track implementation progress

---

## 🎯 Advanced Workflows

### Multi-Environment Management

**Challenge**: Managing development, testing, and production environments.

**Solution**:
1. **Environment-Specific Projects**
   ```
   projects/
   ├── sales_dwh_dev/
   ├── sales_dwh_test/
   └── sales_dwh_prod/
   ```

2. **Configuration Management**
   - Use environment-specific naming conventions
   - Maintain separate Excel workbooks per environment
   - Document environment differences

3. **Promotion Process**
   - Define criteria for environment promotion
   - Use workbook comparison tools
   - Track changes across environments

### Complex Data Lineage Tracking

**Challenge**: Documenting complex data transformations across multiple stages.

**Solution**:
1. **Enhanced Artifact Documentation**
   - Add source system references to Artifact Comments
   - Document transformation logic
   - Link related artifacts across stages

2. **Column-Level Lineage**
   - Use Column Comments to describe transformations
   - Reference source columns in Business Names
   - Document calculated field formulas

3. **External Documentation**
   - Link to transformation code repositories
   - Reference business logic documentation
   - Connect to data governance tools

### Integration with External Tools

**Challenge**: Connecting DWH Creator with other data tools and platforms.

**Solution**:
1. **Export Capabilities**
   - Generate DDL scripts from workbook definitions
   - Create data catalog entries
   - Export to documentation systems

2. **Import Capabilities**
   - Import existing schema definitions
   - Load metadata from data catalogs
   - Sync with version control systems

3. **API Integration**
   - Use workbook data in deployment pipelines
   - Integrate with CI/CD processes
   - Connect to monitoring systems

---

## 💡 Best Practices

### Planning and Design
- **Start Simple**: Begin with core business entities
- **Think Layers**: Design for bronze → silver → gold progression
- **Business First**: Prioritize business understanding over technical details
- **Iterative Approach**: Plan for incremental development

### Documentation Standards
- **Consistent Naming**: Establish and follow naming conventions
- **Clear Descriptions**: Write for business users, not just technical teams
- **Regular Updates**: Keep documentation current with implementation
- **Version Control**: Track changes and maintain history

### AI Feature Usage
- **Review AI Output**: Always validate AI-generated content
- **Customize for Organization**: Adapt AI suggestions to your standards
- **Iterative Improvement**: Refine AI prompts based on results
- **Human Oversight**: Use AI as assistance, not replacement for expertise

### Collaboration Guidelines
- **Clear Ownership**: Assign responsibility for each section
- **Regular Reviews**: Schedule periodic validation sessions
- **Change Management**: Document reasons for modifications
- **Communication**: Keep stakeholders informed of changes

### Quality Assurance
- **Validation Checklists**: Create and use review checklists
- **Cross-Reference Checks**: Verify relationships between sheets
- **Business Validation**: Confirm with domain experts
- **Technical Review**: Validate with implementation teams

### Column Cascading Best Practices
- **Plan Relationships**: Define upstream relationships before cascading
- **Test Incrementally**: Start with single artifacts, then cascade all
- **Validate Data Types**: Check platform-specific type conversions
- **Review Technical Columns**: Ensure stage-specific columns are appropriate
- **Document Customizations**: Track changes to default cascading rules
- **Version Control**: Maintain cascading configuration with project files

---

## 🔧 Troubleshooting Workflows

### Common Workflow Issues

#### Issue: "AI features not working"
**Symptoms**: AI commands fail or return empty results
**Solutions**:
1. Verify OpenAI API key configuration
2. Check internet connectivity
3. Confirm API quota and billing status
4. Review error logs for specific issues

#### Issue: "Excel workbook corruption"
**Symptoms**: Cannot open or save workbook
**Solutions**:
1. Check file permissions
2. Verify Excel installation
3. Use backup copies from previous saves
4. Export data to new workbook

#### Issue: "Inconsistent data model"
**Symptoms**: References between sheets don't match
**Solutions**:
1. Use validation tools to check references
2. Review Stage ID, Artifact ID consistency
3. Verify column relationships
4. Apply naming convention standards

#### Issue: "Performance problems with large workbooks"
**Symptoms**: Slow operations, memory issues
**Solutions**:
1. Split large projects into smaller modules
2. Use efficient column definitions
3. Remove unnecessary data
4. Close other applications during operations

### Workflow Recovery Procedures

#### Corrupted Project Recovery
1. **Assess Damage**
   - Identify which files are affected
   - Determine extent of data loss
   - Check backup availability

2. **Recovery Steps**
   - Restore from most recent backup
   - Recreate missing definitions
   - Validate recovered data
   - Update documentation

3. **Prevention Measures**
   - Implement regular backup schedule
   - Use version control for workbooks
   - Create recovery procedures
   - Train team on backup practices

#### Lost Progress Recovery
1. **Immediate Actions**
   - Stop current work
   - Assess what can be recovered
   - Check auto-save features
   - Review recent activity logs

2. **Recovery Process**
   - Restore from backups
   - Recreate recent changes
   - Validate data integrity
   - Document lessons learned

#### Issue: "Column cascading not working"
**Symptoms**: No columns appear after cascading operation
**Solutions**:
1. **Check Prerequisites**
   - Verify `Upstream Relation` field is populated
   - Confirm `Upstream Artifact` IDs are valid
   - Ensure upstream artifacts have columns defined

2. **Configuration Issues**
   - Check cascading configuration file exists
   - Verify data type mappings are loaded
   - Confirm technical columns configuration

3. **Debugging Steps**
   - Use "Preview Cascading" to see expected results
   - Try cascading single artifact instead of all
   - Check logs for specific error messages
   - Validate upstream artifact relationships

#### Issue: "Wrong data types after cascading"
**Symptoms**: Cascaded columns have incorrect data types
**Solutions**:
1. **Review Platform Mapping**
   - Check source vs target platform settings
   - Verify data type mapping configuration
   - Update mappings for custom types

2. **Configuration Updates**
   - Edit `cascading_config.xlsx` → `DataTypeMappings`
   - Add missing type conversions
   - Save and reload configuration

#### Issue: "Technical columns missing or incorrect"
**Symptoms**: Stage-specific technical columns not added
**Solutions**:
1. **Check Technical Configuration**
   - Verify stage names match configuration
   - Review required vs optional column settings
   - Confirm technical columns for target stage

2. **Update Configuration**
   - Edit `cascading_config.xlsx` → `TechnicalColumns`
   - Add missing stage configurations
   - Set appropriate optional flags

---

## 📈 Workflow Success Metrics

### Project Completion Indicators
- ✅ All stages defined with clear purposes
- ✅ All artifacts mapped to appropriate stages
- ✅ All columns documented with business context
- ✅ AI features successfully applied
- ✅ Stakeholder review completed
- ✅ Documentation validated and approved

### Quality Metrics
- **Coverage**: Percentage of artifacts with complete documentation
- **Consistency**: Adherence to naming conventions and standards
- **Accuracy**: Validation by business and technical stakeholders
- **Completeness**: All required fields populated
- **Usability**: Documentation serves implementation needs

### Process Efficiency
- **Time to Complete**: Track workflow completion times
- **Rework Rate**: Measure changes after initial completion
- **Stakeholder Satisfaction**: Collect feedback on process and results
- **Tool Effectiveness**: Evaluate AI feature impact on productivity

---

**Next Steps**: Ready to dive deeper? Check out our [Advanced Features Guide](advanced-features.md) or [API Documentation](../technical/api-reference.md) for more complex use cases.
