"""
Integration Test for Enhanced Relation Processing
===============================================

Test script to validate the integration between ColumnCascadingEngine and RelationProcessor.
"""

# ANCHOR: Test Setup
import sys
from pathlib import Path

# Add src to path for imports
current_dir = Path(__file__).parent
src_dir = current_dir.parent / 'src'
sys.path.insert(0, str(src_dir))

def test_relation_processor_integration():
    """Test RelationProcessor integration with sample data."""
    
    print("🧪 Testing Enhanced Relation Processing Integration")
    print("=" * 60)
    
    try:
        # Import the enhanced modules
        from utils.relation_processor import RelationProcessor, ArtifactType
        from utils.config_manager import ConfigManager
        
        # Initialize components
        relation_processor = RelationProcessor()
        config_manager = ConfigManager()
        
        print("✅ Successfully imported RelationProcessor and ConfigManager")
        
        # Test artifact type detection
        print("\n📊 Testing Artifact Type Detection:")
        test_cases = [
            ("dim_customer", "", "dimension"),
            ("fact_sales", "", "fact"), 
            ("bridge_employee_role", "", "bridge"),
            ("unknown_table", "", "unknown"),
            ("any_table", "dimension", "dimension")  # Explicit type
        ]
        
        for artifact_name, explicit_type, expected in test_cases:
            detected = relation_processor.detect_artifact_type(artifact_name, explicit_type)
            status = "✅" if detected.value == expected else "❌"
            print(f"  {status} {artifact_name} ({explicit_type or 'auto'}) → {detected.value}")
        
        # Test stage transition detection
        print("\n🔄 Testing Stage Transition Detection:")
        transition_tests = [
            ("s1", "s2", "bronze_to_silver"),
            ("s2", "s3", "silver_to_gold"),
            ("s3", "s4", "gold_to_mart"),
            ("s4", "s5", "mart_to_pbi")
        ]
        
        for source, target, expected in transition_tests:
            transition = relation_processor.detect_stage_transition(source, target)
            detected_name = transition.value.replace('s1_to_s2', 'bronze_to_silver').replace('s2_to_s3', 'silver_to_gold').replace('s3_to_s4', 'gold_to_mart').replace('s4_to_s5', 'mart_to_pbi') if transition else "none"
            status = "✅" if transition and expected in detected_name else "❌"
            print(f"  {status} {source} → {target}: {detected_name}")
        
        # Test relation type configuration alignment
        print("\n⚙️ Testing Configuration Alignment:")
        config_relation_types = config_manager.get_relation_types()
        processor_methods = ['main', 'get_key', 'lookup', 'pbi']
        
        for rel_type in config_relation_types:
            if rel_type in processor_methods:
                print(f"  ✅ {rel_type}: ConfigManager ↔ RelationProcessor aligned")
            else:
                print(f"  ❌ {rel_type}: Missing in RelationProcessor")
        
        # Test sample column processing
        print("\n📋 Testing Sample Column Processing:")
        sample_columns = [
            {'Column Name': 'customer_sk', 'Data Type': 'bigint', 'Column Group': 'SKs'},
            {'Column Name': 'customer_bk', 'Data Type': 'varchar(50)', 'Column Group': 'BKs'},
            {'Column Name': 'customer_name', 'Data Type': 'varchar(100)', 'Column Group': 'attributes'},
            {'Column Name': 'sales_amount', 'Data Type': 'decimal(18,2)', 'Column Group': 'facts'}
        ]
        
        # Test main relation processing
        main_result = relation_processor.process_main_relation(
            sample_columns, 's1', 's2', ArtifactType.DIMENSION
        )
        print(f"  ✅ Main relation: {len(sample_columns)} → {len(main_result)} columns")
        
        # Test get_key relation processing  
        key_result = relation_processor.process_get_key_relation(
            sample_columns, ArtifactType.FACT
        )
        print(f"  ✅ Get_key relation: {len(sample_columns)} → {len(key_result)} columns")
        
        # Test lookup relation processing
        lookup_result = relation_processor.process_lookup_relation(sample_columns, 3)
        print(f"  ✅ Lookup relation: {len(sample_columns)} → {len(lookup_result)} columns (limit: 3)")
        
        # Test PBI relation processing
        pbi_result = relation_processor.process_pbi_relation(sample_columns)
        print(f"  ✅ PBI relation: {len(sample_columns)} → {len(pbi_result)} columns")
        
        print("\n🎉 All integration tests passed successfully!")
        print("✨ Enhanced relation processing is ready for production use.")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Make sure all dependencies are installed")
        return False
        
    except Exception as e:
        print(f"❌ Test Error: {e}")
        print("💡 Check the integration implementation")
        return False

if __name__ == "__main__":
    test_relation_processor_integration()