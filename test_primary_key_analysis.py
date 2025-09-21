"""
Test Primary Key Identification and Source Analysis
=================================================

This test demonstrates the new primary key identification functionality
and the integrated source file analysis workflow.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np

# Add src to path
current_dir = Path.cwd()
src_dir = current_dir / 'src'
sys.path.insert(0, str(src_dir))

from utils.source_analyzer import SourceFileAnalyzer
from utils.source_file_integrator import SourceFileIntegrator

def create_test_data():
    """Create sample test data files for testing."""
    print("Creating test data files...")
    
    # Create test data directory
    test_data_dir = current_dir / "test_data"
    test_data_dir.mkdir(exist_ok=True)
    
    # Sample customer data with clear primary key
    customers_data = {
        'customer_id': range(1, 101),  # Clear primary key
        'customer_code': [f'CUST{i:04d}' for i in range(1, 101)],  # Business key
        'customer_name': [f'Customer {i}' for i in range(1, 101)],
        'email': [f'customer{i}@example.com' for i in range(1, 101)],
        'phone': [f'555-{i:04d}' for i in range(1, 101)],
        'registration_date': pd.date_range('2020-01-01', periods=100, freq='D'),
        'credit_limit': np.random.uniform(1000, 50000, 100).round(2),
        'is_active': np.random.choice([True, False], 100, p=[0.9, 0.1])
    }
    customers_df = pd.DataFrame(customers_data)
    customers_file = test_data_dir / "customers.csv"
    customers_df.to_csv(customers_file, index=False)
    print(f"Created: {customers_file}")
    
    # Sample orders data with composite primary key
    orders_data = {
        'order_id': range(1, 201),
        'customer_id': np.random.randint(1, 101, 200),  # Foreign key
        'order_number': [f'ORD{i:06d}' for i in range(1, 201)],
        'order_date': pd.date_range('2023-01-01', periods=200, freq='H'),
        'total_amount': np.random.uniform(10, 5000, 200).round(2),
        'status': np.random.choice(['pending', 'completed', 'cancelled'], 200, p=[0.3, 0.6, 0.1]),
        'shipping_address': [f'{i} Main St, City' for i in range(1, 201)]
    }
    orders_df = pd.DataFrame(orders_data)
    orders_file = test_data_dir / "orders.xlsx"
    orders_df.to_excel(orders_file, index=False)
    print(f"Created: {orders_file}")
    
    # Sample products data with business key
    products_data = {
        'product_sku': [f'SKU{i:05d}' for i in range(1, 51)],  # Business key that could be primary
        'product_name': [f'Product {i}' for i in range(1, 51)],
        'category': np.random.choice(['Electronics', 'Clothing', 'Books', 'Home'], 50),
        'price': np.random.uniform(5, 500, 50).round(2),
        'weight': np.random.uniform(0.1, 10, 50).round(2),
        'in_stock': np.random.randint(0, 100, 50),
        'supplier_id': np.random.randint(1, 10, 50),
        'description': [f'High quality product {i} with excellent features' for i in range(1, 51)]
    }
    products_df = pd.DataFrame(products_data)
    products_file = test_data_dir / "products.csv"
    products_df.to_csv(products_file, index=False)
    print(f"Created: {products_file}")
    
    return [
        {"file": customers_file, "table": "dim_customer", "expected_pk": ["customer_id"]},
        {"file": orders_file, "table": "fact_orders", "expected_pk": ["order_id"]},
        {"file": products_file, "table": "dim_product", "expected_pk": ["product_sku"]}
    ]

def test_source_analyzer():
    """Test the SourceFileAnalyzer functionality."""
    print("\n" + "="*60)
    print("TESTING SOURCE FILE ANALYZER")
    print("="*60)
    
    # Create test data
    test_files = create_test_data()
    
    # Initialize analyzer
    analyzer = SourceFileAnalyzer()
    
    for test_case in test_files:
        print(f"\nAnalyzing: {test_case['file'].name}")
        print("-" * 40)
        
        # Analyze the file
        analysis = analyzer.analyze_source_file(str(test_case['file']))
        
        # Display results
        print(f"File: {analysis.file_path}")
        print(f"Rows: {analysis.total_rows}")
        print(f"Columns: {analysis.total_columns}")
        print(f"Data Quality Score: {analysis.data_quality_score:.1%}")
        
        # Primary key analysis
        if analysis.recommended_primary_key:
            pk = analysis.recommended_primary_key
            print(f"\\nRecommended Primary Key:")
            print(f"  Columns: {pk.columns}")
            print(f"  Confidence: {pk.confidence_score:.1%}")
            print(f"  Is Composite: {pk.is_composite}")
            print(f"  Reasoning: {pk.reasoning}")
            
            # Check if matches expected
            expected = test_case['expected_pk']
            matches = set(pk.columns) == set(expected)
            print(f"  Expected: {expected}")
            print(f"  Matches Expected: {'✅' if matches else '❌'}")
        else:
            print("\\nNo primary key identified")
        
        # Column group summary
        column_groups = {}
        for col in analysis.columns_metadata:
            group = col.column_group.value
            column_groups[group] = column_groups.get(group, 0) + 1
        
        print(f"\\nColumn Groups:")
        for group, count in column_groups.items():
            print(f"  {group}: {count}")
        
        # Export analysis
        output_file = test_case['file'].parent / f"{test_case['table']}_analysis.xlsx"
        export_success = analyzer.export_analysis_to_excel(analysis, str(output_file))
        print(f"\\nExport Success: {'✅' if export_success else '❌'}")
        if export_success:
            print(f"Exported to: {output_file}")

def test_primary_key_propagation():
    """Test primary key propagation in cascading logic."""
    print("\n" + "="*60)
    print("TESTING PRIMARY KEY PROPAGATION")
    print("="*60)
    
    try:
        # Find workbook path
        workbook_paths = [
            current_dir / "config" / "cascading_config_AdwentureWorks.xlsx",
            current_dir / "cascading_config_AdwentureWorks.xlsx"
        ]
        
        workbook_path = None
        for path in workbook_paths:
            if path.exists():
                workbook_path = str(path)
                break
        
        if not workbook_path:
            print("❌ Could not find workbook for cascading test")
            return
        
        print(f"Using workbook: {workbook_path}")
        
        # Test primary key propagation logic
        from utils.column_cascading import ColumnCascadingEngine
        
        engine = ColumnCascadingEngine(workbook_path)
        
        # Test column ordering with primary keys
        test_columns = [
            {"Column Name": "customer_name", "Column Group": "attributes", "Order": 5},
            {"Column Name": "customer_id", "Column Group": "primary_key", "Order": 10},
            {"Column Name": "customer_code", "Column Group": "BKs", "Order": 8},
            {"Column Name": "__bronze_insertDT", "Column Group": "technical_fields", "Order": 15}
        ]
        
        # Test ordering priority
        for col in test_columns:
            priority = engine._get_column_type_order_priority(
                col["Column Group"], 
                col["Column Name"]
            )
            print(f"{col['Column Name']} ({col['Column Group']}): Priority {priority}")
        
        # Sort by priority
        sorted_cols = sorted(test_columns, 
                           key=lambda x: engine._get_column_type_order_priority(x["Column Group"], x["Column Name"]))
        
        print(f"\\nSorted Order:")
        for i, col in enumerate(sorted_cols):
            print(f"  {i+1}. {col['Column Name']} ({col['Column Group']})")
        
        print("\\n✅ Primary key propagation test completed")
        
    except Exception as e:
        print(f"❌ Primary key propagation test failed: {str(e)}")

def test_integrated_workflow():
    """Test the complete integrated workflow."""
    print("\n" + "="*60)
    print("TESTING INTEGRATED WORKFLOW")
    print("="*60)
    
    try:
        # Find workbook path
        workbook_paths = [
            current_dir / "config" / "cascading_config_AdwentureWorks.xlsx",
            current_dir / "cascading_config_AdwentureWorks.xlsx"
        ]
        
        workbook_path = None
        for path in workbook_paths:
            if path.exists():
                workbook_path = str(path)
                break
        
        if not workbook_path:
            print("❌ Could not find workbook for integration test")
            return
        
        # Use the test data files
        test_data_dir = current_dir / "test_data"
        customers_file = test_data_dir / "customers.csv"
        
        if not customers_file.exists():
            print("❌ Test data not found. Run create_test_data() first.")
            return
        
        print(f"Testing with: {customers_file}")
        
        # Initialize integrator
        integrator = SourceFileIntegrator(workbook_path)
        
        # Process the file
        print("\\nProcessing source file...")
        result = integrator.process_source_file(
            source_file_path=str(customers_file),
            table_name="test_dim_customer",
            stage_name="1_bronze",
            artifact_type="dimension",
            include_ai_analysis=True,
            update_cascading_config=False,  # Don't actually update for test
            apply_cascading=False  # Don't apply cascading for test
        )
        
        if result['success']:
            print("✅ Integrated workflow completed successfully!")
            
            # Display summary
            analysis = result['analysis']
            print(f"\\nAnalysis Summary:")
            print(f"  File: {analysis.file_path}")
            print(f"  Rows: {analysis.total_rows}")
            print(f"  Columns: {analysis.total_columns}")
            print(f"  Data Quality: {analysis.data_quality_score:.1%}")
            
            if analysis.recommended_primary_key:
                pk = analysis.recommended_primary_key
                print(f"  Primary Key: {pk.columns} (confidence: {pk.confidence_score:.1%})")
            
            # Column configuration
            column_config = result['column_config']
            pk_columns = [c for c in column_config if c['Column Group'] == 'primary_key']
            print(f"  Primary Key Columns in Config: {len(pk_columns)}")
            for pk_col in pk_columns:
                print(f"    - {pk_col['Column Name']}")
            
            # Report
            report = result['report']
            recommendations = report.get('recommendations', [])
            print(f"  Recommendations: {len(recommendations)}")
            for rec in recommendations:
                print(f"    - {rec}")
            
        else:
            print(f"❌ Integrated workflow failed: {result.get('error', 'Unknown error')}")
        
    except Exception as e:
        print(f"❌ Integrated workflow test failed: {str(e)}")

def main():
    """Run all tests."""
    print("🔍 PRIMARY KEY IDENTIFICATION & SOURCE ANALYSIS TESTS")
    print("=" * 80)
    
    try:
        # Test 1: Source File Analyzer
        test_source_analyzer()
        
        # Test 2: Primary Key Propagation
        test_primary_key_propagation()
        
        # Test 3: Integrated Workflow
        test_integrated_workflow()
        
        print("\n" + "=" * 80)
        print("🎉 ALL TESTS COMPLETED!")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Test suite failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()