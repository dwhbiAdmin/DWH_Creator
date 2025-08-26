"""
DWH Creator - Main Entry Point
==============================

Main application entry point for the Data Warehouse Creator tool.

Usage:
    python main.py [options]

Options:
    --console     : Run in console mode
    --gui         : Run with GUI interface  
    --project     : Specify project path
    --help        : Show help information
"""

import sys
import argparse
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="DWH Creator - Data Warehouse Creation Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--console", 
        action="store_true",
        help="Run in console mode"
    )
    
    parser.add_argument(
        "--gui",
        action="store_true", 
        help="Run with GUI interface"
    )
    
    parser.add_argument(
        "--project",
        type=str,
        help="Specify project path to open"
    )
    
    return parser.parse_args()

def main():
    """Main application entry point."""
    print("🏗️  DWH Creator - Data Warehouse Creation Tool")
    print("=" * 50)
    
    args = parse_arguments()
    
    if args.console:
        print("Starting in console mode...")
        # TODO: Initialize console interface
    elif args.gui:
        print("Starting GUI interface...")
        # TODO: Initialize GUI interface
    else:
        print("Please specify --console or --gui mode")
        print("Use --help for more information")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
