"""
DWH Creator - Session Resume Helper Script
=========================================

Quick script to understand current project state and resume work efficiently.
Run this at the start of each coding session to avoid wasting time.

Usage:
    python scripts/resume_work.py
"""

import pandas as pd
import subprocess
import os
from pathlib import Path
from datetime import datetime

def run_git_command(command):
    """Run git command and return output."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=".")
        return result.stdout.strip() if result.returncode == 0 else f"Error: {result.stderr}"
    except Exception as e:
        return f"Error running command: {e}"

def check_file_status(file_path):
    """Check if file exists and get modification time."""
    if os.path.exists(file_path):
        mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
        return f"✓ Last modified: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}"
    else:
        return "✗ File not found"

def show_current_state():
    """Display comprehensive project state."""
    
    print("=" * 60)
    print("🚀 DWH CREATOR - SESSION RESUME")
    print("=" * 60)
    
    # 1. Git Status
    print("\n📋 GIT STATUS")
    print("-" * 30)
    print("Current branch:", run_git_command("git branch --show-current"))
    print("Status:", run_git_command("git status --porcelain") or "Clean working directory")
    
    print("\nRecent commits:")
    recent_commits = run_git_command("git log --oneline -5")
    for line in recent_commits.split('\n')[:5]:
        if line.strip():
            print(f"  {line}")
    
    # 2. Project Files Status
    print(f"\n📁 PROJECT FILES")
    print("-" * 30)
    
    # Define key project files
    project_dir = r"c:\Users\bezas\repos\DWH_Creator\_DWH_Projects\Project_AdwentureWorks"
    workbench_path = f"{project_dir}\\2_workbench\\workbench_AdwentureWorks.xlsx"
    config_path = f"{project_dir}\\2_workbench\\cascading_config_AdwentureWorks.xlsx"
    csv_dir = f"{project_dir}\\1_sources"
    
    files_to_check = {
        "Workbench": workbench_path,
        "Config": config_path,
        "Customer CSV": f"{csv_dir}\\customer.csv",
        "Product CSV": f"{csv_dir}\\product.csv", 
        "Orders CSV": f"{csv_dir}\\orders.csv"
    }
    
    for name, path in files_to_check.items():
        print(f"{name:12}: {check_file_status(path)}")
    
    # 3. Current Workbench State
    print(f"\n📊 WORKBENCH STATE")
    print("-" * 30)
    
    try:
        if os.path.exists(workbench_path):
            # Check Columns sheet
            df_columns = pd.read_excel(workbench_path, sheet_name='Columns')
            df_artifacts = pd.read_excel(workbench_path, sheet_name='Artifacts')
            
            print(f"Total columns: {len(df_columns)}")
            
            if len(df_columns) > 0:
                column_ids = df_columns['Column ID'].dropna().head(10).tolist()
                print(f"Column IDs: {column_ids}")
                
                # Check if proper c1, c2, c3 format
                proper_format = all(str(cid).startswith('c') and str(cid)[1:].isdigit() for cid in df_columns['Column ID'].dropna())
                print(f"Proper c1,c2,c3 format: {'✓' if proper_format else '✗'}")
                
                # Primary keys
                pk_count = len(df_columns[df_columns['Column Group'] == 'Primary Key'])
                print(f"Primary key columns: {pk_count}")
                
                # Artifacts
                source_artifacts = df_artifacts[df_artifacts['Stage ID'] == 's0']
                print(f"Source artifacts: {len(source_artifacts)} (IDs: {source_artifacts['Artifact ID'].tolist()})")
            else:
                print("⚠️ No columns found - workbench may be empty")
        else:
            print("⚠️ Workbench file not found")
            
    except Exception as e:
        print(f"⚠️ Error reading workbench: {e}")
    
    # 4. Established Patterns Reminder
    print(f"\n🎯 ESTABLISHED PATTERNS (DON'T RECREATE)")
    print("-" * 30)
    print("✓ Column ID sequencing: ColumnCascadingEngine._get_next_column_id()")
    print("✓ Format: c1, c2, c3, c4... (NOT C_artifact_column)")
    print("✓ Artifact IDs: a1, a2, a3... (NOT c1, c2)")
    print("✓ Artifact names: customer, product, orders (NO _table suffix)")
    print("✓ Stage IDs: s0, s1, s2... for stage references")
    print("✓ Column Group: Only 'Primary Key' for PKs, empty for others")
    
    # 5. Quick Commands
    print(f"\n⚡ QUICK COMMANDS")
    print("-" * 30)
    print("Check established sequencing:")
    print("  from src.utils.column_cascading import ColumnCascadingEngine")
    print("  engine = ColumnCascadingEngine(workbench_path, config_path)")
    print("  column_id = engine._get_next_column_id()  # Returns c1, c2, c3...")
    
    print("\nView session notes:")
    print("  cat SESSION_NOTES.md")
    
    print("\nView patterns:")
    print("  cat PATTERNS.md")
    
    print("\nView commands:")
    print("  cat COMMANDS.md")
    
    # 6. Session Notes Summary
    print(f"\n📝 LAST SESSION SUMMARY")
    print("-" * 30)
    try:
        if os.path.exists("SESSION_NOTES.md"):
            with open("SESSION_NOTES.md", 'r', encoding='utf-8') as f:
                content = f.read()
                # Extract the latest session info
                lines = content.split('\n')
                session_found = False
                summary_lines = []
                for line in lines:
                    if "## 2025-" in line and not session_found:
                        session_found = True
                        summary_lines.append(line)
                    elif session_found and line.startswith("**Status**"):
                        summary_lines.append(line)
                        break
                    elif session_found:
                        summary_lines.append(line)
                        if len(summary_lines) > 10:  # Limit output
                            break
                
                for line in summary_lines[:8]:
                    print(line)
                if len(summary_lines) > 8:
                    print("... (see SESSION_NOTES.md for full details)")
        else:
            print("No session notes found - this is the first session")
    except Exception as e:
        print(f"Error reading session notes: {e}")
    
    print(f"\n✨ Ready to continue! Check PATTERNS.md before building anything new.")
    print("=" * 60)

if __name__ == "__main__":
    show_current_state()