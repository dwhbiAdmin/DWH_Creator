"""
Source File Analysis CLI
=======================

Command-line interface for analyzing source files and integrating them
into the DWH Creator workflow with primary key identification.

Usage:
    python analyze_source.py <source_file> <table_name> [options]

Example:
    python analyze_source.py data/customers.csv dim_customer --stage=1_bronze --type=dimension
"""

import argparse
import sys
from pathlib import Path
import json

# Add src to path for imports
current_dir = Path(__file__).parent
src_dir = current_dir.parent
sys.path.insert(0, str(src_dir))

from utils.source_file_integrator import SourceFileIntegrator
from utils.logger import Logger

def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Analyze source files and integrate with DWH Creator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic analysis
  python analyze_source.py data/customers.csv dim_customer
  
  # With specific stage and type
  python analyze_source.py data/orders.xlsx fact_orders --stage=1_bronze --type=fact
  
  # Skip cascading update
  python analyze_source.py data/products.csv dim_product --no-cascading
  
  # Batch processing with JSON config
  python analyze_source.py --batch batch_config.json
        """
    )
    
    # Main arguments
    parser.add_argument(
        'source_file',
        nargs='?',
        help='Path to the source file to analyze'
    )
    
    parser.add_argument(
        'table_name',
        nargs='?',
        help='Name for the target table/artifact'
    )
    
    # Optional arguments
    parser.add_argument(
        '--stage',
        default='1_bronze',
        help='Target stage name (default: 1_bronze)'
    )
    
    parser.add_argument(
        '--type',
        default='dimension',
        help='Artifact type: dimension, fact, etc. (default: dimension)'
    )
    
    parser.add_argument(
        '--workbook',
        help='Path to the main workbook (if not using default)'
    )
    
    parser.add_argument(
        '--config',
        help='Path to configuration file (if not using default)'
    )
    
    parser.add_argument(
        '--no-ai',
        action='store_true',
        help='Skip AI-powered analysis'
    )
    
    parser.add_argument(
        '--no-cascading',
        action='store_true',
        help='Skip cascading configuration update'
    )
    
    parser.add_argument(
        '--no-apply',
        action='store_true',
        help='Skip applying cascading logic'
    )
    
    parser.add_argument(
        '--batch',
        help='JSON file with batch processing configuration'
    )
    
    parser.add_argument(
        '--output',
        help='Custom output path for results'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Initialize logger
    logger = Logger()
    
    try:
        # Determine workbook path
        workbook_path = args.workbook
        if not workbook_path:
            # Try to find default workbook
            current_dir = Path.cwd()
            possible_paths = [
                current_dir / "config" / "workbench.xlsx",
                current_dir / "workbench.xlsx",
                current_dir.parent / "config" / "workbench.xlsx"
            ]
            
            for path in possible_paths:
                if path.exists():
                    workbook_path = str(path)
                    break
            
            if not workbook_path:
                logger.error("Could not find workbook. Please specify --workbook path")
                return 1
        
        # Initialize integrator
        integrator = SourceFileIntegrator(workbook_path, args.config)
        
        # Batch processing
        if args.batch:
            return process_batch(integrator, args.batch, args)
        
        # Single file processing
        if not args.source_file or not args.table_name:
            parser.error("source_file and table_name are required for single file processing")
        
        return process_single_file(integrator, args)
        
    except Exception as e:
        logger.error(f"CLI error: {str(e)}")
        return 1

def process_single_file(integrator: SourceFileIntegrator, args) -> int:
    """Process a single source file."""
    logger = Logger()
    
    try:
        logger.info(f"Starting analysis of: {args.source_file}")
        logger.info(f"Target table: {args.table_name}")
        logger.info(f"Stage: {args.stage}, Type: {args.type}")
        
        # Process the file
        result = integrator.process_source_file(
            source_file_path=args.source_file,
            table_name=args.table_name,
            stage_name=args.stage,
            artifact_type=args.type,
            include_ai_analysis=not args.no_ai,
            update_cascading_config=not args.no_cascading,
            apply_cascading=not args.no_apply
        )
        
        if result['success']:
            logger.info("✅ Processing completed successfully!")
            
            # Print summary
            print("\\n" + "="*60)
            print("SOURCE FILE ANALYSIS SUMMARY")
            print("="*60)
            
            analysis = result['analysis']
            print(f"File: {analysis.file_path}")
            print(f"Rows: {analysis.total_rows:,}")
            print(f"Columns: {analysis.total_columns}")
            print(f"Data Quality: {analysis.data_quality_score:.1%}")
            
            # Primary key information
            if analysis.recommended_primary_key:
                pk = analysis.recommended_primary_key
                pk_type = "Composite" if pk.is_composite else "Single"
                print(f"\\nPrimary Key ({pk_type}):")
                print(f"  Columns: {', '.join(pk.columns)}")
                print(f"  Confidence: {pk.confidence_score:.1%}")
                print(f"  Reasoning: {pk.reasoning}")
            else:
                print("\\nPrimary Key: None identified")
            
            # Column summary
            column_stats = result['report']['column_statistics']
            print(f"\\nColumn Distribution:")
            print(f"  Primary Keys: {column_stats['primary_key_columns']}")
            print(f"  Business Keys: {column_stats['business_key_columns']}")
            print(f"  Attributes: {column_stats['attribute_columns']}")
            print(f"  Technical: {column_stats['technical_columns']}")
            
            # Recommendations
            recommendations = result['report']['recommendations']
            if recommendations:
                print(f"\\nRecommendations:")
                for i, rec in enumerate(recommendations, 1):
                    print(f"  {i}. {rec}")
            
            # Output file
            if result['output_path']:
                print(f"\\nDetailed results: {result['output_path']}")
            
            print("="*60)
            return 0
            
        else:
            logger.error(f"❌ Processing failed: {result.get('error', 'Unknown error')}")
            return 1
            
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        return 1

def process_batch(integrator: SourceFileIntegrator, batch_file: str, args) -> int:
    """Process multiple files from batch configuration."""
    logger = Logger()
    
    try:
        # Load batch configuration
        with open(batch_file, 'r') as f:
            batch_config = json.load(f)
        
        source_files = batch_config.get('source_files', [])
        if not source_files:
            logger.error("No source files found in batch configuration")
            return 1
        
        logger.info(f"Starting batch processing of {len(source_files)} files")
        
        # Process files
        results = integrator.batch_process_source_files(
            source_files,
            include_ai_analysis=not args.no_ai,
            update_cascading_config=not args.no_cascading,
            apply_cascading=not args.no_apply
        )
        
        # Print summary
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        print("\\n" + "="*60)
        print("BATCH PROCESSING SUMMARY")
        print("="*60)
        print(f"Total files: {len(results)}")
        print(f"Successful: {len(successful)}")
        print(f"Failed: {len(failed)}")
        
        if failed:
            print("\\nFailed files:")
            for result in failed:
                print(f"  - {result['source_file']}: {result.get('error', 'Unknown error')}")
        
        if successful:
            print("\\nSuccessful files:")
            for result in successful:
                analysis = result['analysis']
                pk_info = "✓" if analysis.recommended_primary_key else "✗"
                print(f"  - {result['table_name']} (PK: {pk_info}, Quality: {analysis.data_quality_score:.1%})")
        
        print("="*60)
        
        return 0 if len(failed) == 0 else 1
        
    except Exception as e:
        logger.error(f"Batch processing error: {str(e)}")
        return 1

def create_batch_example():
    """Create an example batch configuration file."""
    example_config = {
        "source_files": [
            {
                "path": "data/customers.csv",
                "table_name": "dim_customer",
                "stage_name": "1_bronze",
                "artifact_type": "dimension"
            },
            {
                "path": "data/orders.xlsx",
                "table_name": "fact_orders",
                "stage_name": "1_bronze",
                "artifact_type": "fact"
            },
            {
                "path": "data/products.json",
                "table_name": "dim_product",
                "stage_name": "1_bronze",
                "artifact_type": "dimension"
            }
        ],
        "global_settings": {
            "include_ai_analysis": True,
            "update_cascading_config": True,
            "apply_cascading": True
        }
    }
    
    with open("batch_example.json", "w") as f:
        json.dump(example_config, f, indent=2)
    
    print("Created batch_example.json with sample configuration")

if __name__ == "__main__":
    # If run with --create-example, create batch example and exit
    if len(sys.argv) == 2 and sys.argv[1] == '--create-example':
        create_batch_example()
        sys.exit(0)
    
    sys.exit(main())