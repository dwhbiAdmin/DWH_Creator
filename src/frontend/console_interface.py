"""
Console Interface for DWH Creator
=================================

Provides a command-line interface for the DWH Creator application.
Implements the main menu structure and user interaction flow.
"""

# ANCHOR: Imports and Dependencies

import os
import sys
from pathlib import Path

# Add src to path for imports
current_dir = Path(__file__).parent
src_dir = current_dir.parent
sys.path.insert(0, str(src_dir))

from backend.A_project_manager import ProjectManager
from backend.B_workbench_manager import WorkbenchManager
from utils.logger import Logger
from utils.Z_app_configurations import AppConfig

# ANCHOR: ConsoleInterface Class Definition

class ConsoleInterface:
    """
    Console-based user interface for DWH Creator.
    """
    
    # ANCHOR: Initialization and Setup
    def __init__(self):
        """Initialize the console interface."""
        self.project_manager = ProjectManager()
        self.logger = Logger()
        self.current_project_path = None
        self.workbench_manager = None
        self.app_config = AppConfig()
        self.openai_api_key = self.app_config.get_openai_api_key()
        
    # ANCHOR: Display and Menu Methods
    def display_header(self):
        """Display application header."""
        print("\n" + "=" * 60)
        print("🏗️  DWH Creator - Data Warehouse Creation Tool")
        print("   Console Interface v1.0")
        print("=" * 60)
        
    def display_main_menu(self):
        """Display the main menu options."""
        print("\n📋 Main Menu:")
        print("1. Create New Project")
        print("2. Open Existing Project")
        if self.current_project_path:
            print("3. Workbench Operations")
            print("4. Generate Artifacts")
            print("5. Documentation")
        print("0. Exit")
        print("-" * 40)
        
    def get_user_choice(self, max_option: int) -> int:
        """
        Get user menu choice with validation.
        
        Args:
            max_option: Maximum valid option number
            
        Returns:
            int: User's choice
        """
        while True:
            try:
                choice = input(f"Enter your choice (0-{max_option}): ").strip()
                choice_int = int(choice)
                if 0 <= choice_int <= max_option:
                    return choice_int
                else:
                    print(f"❌ Please enter a number between 0 and {max_option}")
            except ValueError:
                print("❌ Please enter a valid number")
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                sys.exit(0)
                
    # ANCHOR: Project Management Handlers
    def handle_new_project(self):
        """Handle new project creation."""
        print("\n🆕 Create New Project")
        print("-" * 30)
        
        # Get project name
        while True:
            project_name = input("Enter project name: ").strip()
            if project_name:
                # Remove invalid characters for folder names
                project_name = "".join(c for c in project_name if c.isalnum() or c in (' ', '-', '_')).strip()
                if project_name:
                    break
            print("❌ Please enter a valid project name")
            
        # Get project location (optional)
        print(f"\nDefault location: {self.project_manager.get_default_projects_path()}")
        custom_path = input("Enter custom path (or press Enter for default): ").strip()
        
        base_path = custom_path if custom_path else None
        
        # Create the project
        print(f"\n🔨 Creating project '{project_name}'...")
        try:
            project_path = self.project_manager.create_new_project(project_name, base_path)
            if project_path:
                print(f"✅ Project created successfully!")
                print(f"📁 Project location: {project_path}")
                self.current_project_path = project_path
                # Initialize workbench manager for this project
                self.workbench_manager = WorkbenchManager(project_path, self.openai_api_key)
                
                # Ask if user wants to open Excel workbook
                print("\n⚠️  Note: If you open the Excel workbook, you'll need to close it before import operations")
                open_excel = input("📊 Open Excel workbook now? (y/n): ").strip().lower()
                if open_excel in ['y', 'yes']:
                    self.project_manager.open_excel_workbook(project_path)
                    
            else:
                print("❌ Failed to create project")
        except Exception as e:
            print(f"❌ Error creating project: {str(e)}")
            
    def handle_open_project(self):
        """Handle opening existing project."""
        print("\n📂 Open Existing Project")
        print("-" * 30)
        
        # Show available projects
        available_projects = self.project_manager.list_available_projects()
        
        if not available_projects:
            print("❌ No existing projects found")
            print(f"📁 Default projects location: {self.project_manager.get_default_projects_path()}")
            return
            
        print("📋 Available projects:")
        for i, project in enumerate(available_projects, 1):
            print(f"{i}. {project['name']} ({project['path']})")
            
        print(f"{len(available_projects) + 1}. Browse for different location")
        print("0. Back to main menu")
        
        max_choice = len(available_projects) + 1
        choice = self.get_user_choice(max_choice)
        
        if choice == 0:
            return
        elif choice == len(available_projects) + 1:
            # Browse for custom location
            custom_path = input("Enter project path: ").strip()
            if custom_path and os.path.exists(custom_path):
                project_path = custom_path
            else:
                print("❌ Invalid path")
                return
        else:
            # Select from available projects
            project_path = available_projects[choice - 1]['path']
            
        # Open the project
        print(f"\n📂 Opening project: {project_path}")
        try:
            if self.project_manager.open_existing_project(project_path):
                print("✅ Project opened successfully!")
                self.current_project_path = project_path
                # Initialize workbench manager for this project
                self.workbench_manager = WorkbenchManager(project_path, self.openai_api_key)
                
                # Ask if user wants to open Excel workbook
                print("\n⚠️  Note: If you open the Excel workbook, you'll need to close it before import operations")
                open_excel = input("📊 Open Excel workbook? (y/n): ").strip().lower()
                if open_excel in ['y', 'yes']:
                    self.project_manager.open_excel_workbook(project_path)
            else:
                print("❌ Failed to open project")
        except Exception as e:
            print(f"❌ Error opening project: {str(e)}")
            
    # ANCHOR: Status and Utility Methods
    def show_project_status(self):
        """Show current project status."""
        if self.current_project_path:
            print(f"\n📊 Current Project: {os.path.basename(self.current_project_path)}")
            print(f"📁 Location: {self.current_project_path}")
        else:
            print("\n❌ No project currently open")
            
    # ANCHOR: Main Application Loop
    def run(self):
        """Main application loop."""
        self.display_header()
        
        while True:
            self.show_project_status()
            self.display_main_menu()
            
            # Determine max option based on whether project is open
            max_option = 5 if self.current_project_path else 2
            choice = self.get_user_choice(max_option)
            
            if choice == 0:
                print("\n👋 Thank you for using DWH Creator!")
                break
            elif choice == 1:
                self.handle_new_project()
            elif choice == 2:
                self.handle_open_project()
            elif choice == 3 and self.current_project_path:
                self.handle_workbench_operations()
            elif choice == 4 and self.current_project_path:
                print("\n🚧 Generate Artifacts - Coming soon!")
                input("Press Enter to continue...")
            elif choice == 5 and self.current_project_path:
                print("\n🚧 Documentation - Coming soon!")
                input("Press Enter to continue...")
                
    # ANCHOR: Workbench Operations Handler
    def handle_workbench_operations(self):
        """Handle workbench operations submenu."""
        if not self.workbench_manager:
            print("❌ Workbench manager not initialized")
            input("Press Enter to continue...")
            return
            
        while True:
            print(f"\n🔧 Workbench Operations")
            print("-" * 30)
            print("1. Import Raw files from 1_sources")
            print("2. Generate AI Comments (Artifacts)")
            print("3. Generate AI Comments (Columns)")
            print("4. Generate Business Column Names")
            print("5. Cascade Operations")
            print("6. Sync & Validate")
            print("7. Save Workbook")
            print("0. Back to Main Menu")
            print("-" * 30)
            
            try:
                choice = int(input("Enter your choice (0-7): "))
                
                if choice == 0:
                    break
                elif choice == 1:
                    self._handle_import_assign()
                elif choice == 2:
                    self._handle_artifact_ai_comments()
                elif choice == 3:
                    self._handle_column_ai_comments()
                elif choice == 4:
                    self._handle_readable_column_names()
                elif choice == 5:
                    self._handle_cascade_operations()
                elif choice == 6:
                    self._handle_sync_validate()
                elif choice == 7:
                    self._handle_save_workbook()
                else:
                    print("❌ Please enter a valid number (0-7)")
                    
            except ValueError:
                print("❌ Please enter a valid number")
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
                
    # ANCHOR: Workbench Operation Helper Methods
    def _handle_open_stages(self):
        """Handle opening stages sheet."""
        print("\n📊 Opening Stages Sheet...")
        if self.workbench_manager.open_stages_sheet():
            print("✅ Stages sheet opened successfully!")
        else:
            print("❌ Failed to open stages sheet")
        input("Press Enter to continue...")
        
    def _handle_open_artifacts(self):
        """Handle opening artifacts sheet."""
        print("\n📊 Opening Artifacts Sheet...")
        if self.workbench_manager.open_artifacts_sheet():
            print("✅ Artifacts sheet opened successfully!")
        else:
            print("❌ Failed to open artifacts sheet")
        input("Press Enter to continue...")
        
    def _handle_open_columns(self):
        """Handle opening columns sheet."""
        print("\n📊 Opening Columns Sheet...")
        if self.workbench_manager.open_columns_sheet():
            print("✅ Columns sheet opened successfully!")
        else:
            print("❌ Failed to open columns sheet")
        input("Press Enter to continue...")
        
    def _handle_import_assign(self):
        """Handle import/assign operation."""
        print("\n📥 Import Raw files from 1_data_sources")
        print("-" * 40)
        
        sources_path = os.path.join(self.current_project_path, "1_data_sources")
        if not os.path.exists(sources_path):
            print(f"❌ Sources folder not found: {sources_path}")
            input("Press Enter to continue...")
            return
        
        # Check for CSV files
        import glob
        csv_files = glob.glob(os.path.join(sources_path, "*.csv"))
        if not csv_files:
            print(f"❌ No CSV files found in {sources_path}")
            print("Please add CSV files to the 1_sources folder first")
            input("Press Enter to continue...")
            return
        
        print(f"📁 Found {len(csv_files)} CSV files:")
        for csv_file in csv_files:
            print(f"  - {os.path.basename(csv_file)}")
        
        print("\n⚠️  Important: Make sure the Excel workbook is closed before proceeding")
        proceed = input("🔄 Proceed with import/assign? (y/n): ").strip().lower()
        if proceed in ['y', 'yes']:
            print("\n⏳ Processing CSV files...")
            if self.workbench_manager.import_assign_columns():
                print("✅ Import/Assign completed successfully!")
            else:
                print("❌ Import/Assign failed")
                print("💡 Tip: If you see file locking errors, close Excel and try again")
        
        input("Press Enter to continue...")
    
    # ANCHOR: AI Comment Generation Handlers
    def _handle_artifact_ai_comments(self):
        """Handle AI comment generation for artifacts."""
        print("\n🤖 Generate AI Comments for Artifacts")
        print("-" * 40)
        
        if not self.workbench_manager.is_ai_available():
            print("❌ AI comment generation not available")
            print("💡 Please ensure OpenAI API key is configured in config/config.ini")
            input("Press Enter to continue...")
            return
        
        proceed = input("🔄 Generate AI comments for all artifacts? (y/n): ").strip().lower()
        if proceed in ['y', 'yes']:
            print("\n⏳ Generating AI comments for artifacts...")
            if self.workbench_manager.generate_artifact_ai_comments():
                print("✅ Artifact AI comments generated successfully!")
            else:
                print("❌ Failed to generate artifact AI comments")
                print("💡 Check console output for details")
        
        input("Press Enter to continue...")
    
    def _handle_column_ai_comments(self):
        """Handle AI comment generation for columns."""
        print("\n🤖 Generate AI Comments for Columns")
        print("-" * 40)
        
        if not self.workbench_manager.is_ai_available():
            print("❌ AI comment generation not available")
            print("💡 Please ensure OpenAI API key is configured in config/config.ini")
            input("Press Enter to continue...")
            return
        
        proceed = input("🔄 Generate AI comments for all columns? (y/n): ").strip().lower()
        if proceed in ['y', 'yes']:
            print("\n⏳ Generating AI comments for columns...")
            if self.workbench_manager.generate_column_ai_comments():
                print("✅ Column AI comments generated successfully!")
            else:
                print("❌ Failed to generate column AI comments")
                print("💡 Check console output for details")
        
        input("Press Enter to continue...")
    
    def _handle_readable_column_names(self):
        """Handle business column names generation."""
        print("\n🏷️  Generate Business Column Names")
        print("-" * 40)
        
        if not self.workbench_manager.is_ai_available():
            print("❌ AI business name generation not available")
            print("💡 Please ensure OpenAI API key is configured in config/config.ini")
            input("Press Enter to continue...")
            return
        
        proceed = input("🔄 Generate business names for all columns? (y/n): ").strip().lower()
        if proceed in ['y', 'yes']:
            print("\n⏳ Generating business column names...")
            if self.workbench_manager.generate_readable_column_names():
                print("✅ Business column names generated successfully!")
            else:
                print("❌ Failed to generate business column names")
                print("💡 Check console output for details")
        
        input("Press Enter to continue...")
    
    # ANCHOR: Additional Operations Handlers
    def _handle_cascade_operations(self):
        """Handle cascade operations."""
        while True:
            print("\n🔄 Cascade Operations")
            print("-" * 25)
            print("1. Cascade All Artifacts")
            print("2. Cascade Specific Artifact")
            print("3. Preview Cascading")
            print("4. Create Workbench Configuration")
            print("5. List Artifacts with Upstream Relations")
            print("0. Back to Workbench Menu")
            print("-" * 25)
            
            choice = self.get_user_choice(5)
            
            if choice == 0:
                break
            elif choice == 1:
                self._cascade_all_artifacts()
            elif choice == 2:
                self._cascade_specific_artifact()
            elif choice == 3:
                self._preview_cascading()
            elif choice == 4:
                self._create_cascading_config()
            elif choice == 5:
                self._list_artifacts_with_upstream()
    
    def _cascade_all_artifacts(self):
        """Handle cascading all artifacts."""
        print("\n🔄 Cascading All Artifacts")
        print("-" * 30)
        
        try:
            # Get artifacts with upstream relationships
            artifacts = self.workbench_manager.get_artifacts_with_upstream()
            
            if not artifacts:
                print("❌ No artifacts with upstream relationships found")
                input("Press Enter to continue...")
                return
            
            print(f"Found {len(artifacts)} artifacts with upstream relationships:")
            for artifact in artifacts:
                print(f"  • {artifact['Artifact Name']} (ID: {artifact['Artifact ID']}) - {artifact['Upstream Relation']}")
            
            print("\n⚠️  This will cascade columns for all these artifacts.")
            confirm = input("Continue? (y/N): ").strip().lower()
            
            if confirm == 'y':
                print("\n⏳ Processing cascading operations...")
                success = self.workbench_manager.cascade_columns()
                
                if success:
                    print("✅ Column cascading completed successfully!")
                else:
                    print("❌ Column cascading failed. Check logs for details.")
            else:
                print("❌ Operation cancelled")
                
        except Exception as e:
            print(f"❌ Error during cascading: {str(e)}")
        
        input("Press Enter to continue...")
    
    def _cascade_specific_artifact(self):
        """Handle cascading for a specific artifact."""
        print("\n🎯 Cascade Specific Artifact")
        print("-" * 32)
        
        try:
            # Get artifacts with upstream relationships
            artifacts = self.workbench_manager.get_artifacts_with_upstream()
            
            if not artifacts:
                print("❌ No artifacts with upstream relationships found")
                input("Press Enter to continue...")
                return
            
            print("Available artifacts with upstream relationships:")
            for i, artifact in enumerate(artifacts, 1):
                print(f"{i}. {artifact['Artifact Name']} (ID: {artifact['Artifact ID']}) - {artifact['Upstream Relation']}")
            
            print("0. Cancel")
            
            while True:
                try:
                    choice = int(input(f"\nSelect artifact (0-{len(artifacts)}): "))
                    if choice == 0:
                        print("❌ Operation cancelled")
                        break
                    elif 1 <= choice <= len(artifacts):
                        selected_artifact = artifacts[choice - 1]
                        artifact_id = selected_artifact['Artifact ID']
                        
                        print(f"\n⏳ Cascading columns for: {selected_artifact['Artifact Name']}")
                        success = self.workbench_manager.cascade_columns_for_artifact(artifact_id)
                        
                        if success:
                            print("✅ Column cascading completed successfully!")
                        else:
                            print("❌ Column cascading failed. Check logs for details.")
                        break
                    else:
                        print(f"❌ Please enter a number between 0 and {len(artifacts)}")
                except ValueError:
                    print("❌ Please enter a valid number")
                    
        except Exception as e:
            print(f"❌ Error during cascading: {str(e)}")
        
        input("Press Enter to continue...")
    
    def _preview_cascading(self):
        """Show preview of cascading operations."""
        print("\n�️  Preview Cascading")
        print("-" * 21)
        
        try:
            # Get artifacts with upstream relationships
            artifacts = self.workbench_manager.get_artifacts_with_upstream()
            
            if not artifacts:
                print("❌ No artifacts with upstream relationships found")
                input("Press Enter to continue...")
                return
            
            print("Cascading Preview:")
            for artifact in artifacts:
                artifact_id = artifact['Artifact ID']
                preview = self.workbench_manager.get_cascading_preview(artifact_id)
                
                print(f"\n📋 {artifact['Artifact Name']} (ID: {artifact_id})")
                print(f"   Stage: {artifact['Stage Name']}")
                print(f"   Upstream Relation: {artifact['Upstream Relation']}")
                
                if 'error' in preview:
                    print(f"   ❌ {preview['error']}")
                elif 'message' in preview:
                    print(f"   ℹ️  {preview['message']}")
                else:
                    print(f"   📝 {preview.get('preview_note', 'Would cascade columns')}")
                    
        except Exception as e:
            print(f"❌ Error generating preview: {str(e)}")
        
        input("Press Enter to continue...")
    
    def _create_cascading_config(self):
        """Create workbench configuration file using new WorkbenchConfigurationManager."""
        print("\n⚙️  Create Workbench Configuration")
        print("-" * 38)
        
        try:
            print("This will create a configuration file with:")
            print("• Complete AdventureWorks example structure")
            print("• Stages, technical columns, relations, and data mappings")
            print("• Ready-to-use default configuration")
            
            confirm = input("\nCreate configuration file? (y/N): ").strip().lower()
            
            if confirm == 'y':
                print("\n⏳ Creating configuration file...")
                
                # Import the new WorkbenchConfigurationManager
                import sys
                from pathlib import Path
                current_dir = Path(__file__).parent
                src_dir = current_dir.parent
                sys.path.insert(0, str(src_dir))
                from utils.A_project_config_setup import WorkbenchConfigurationManager
                
                # Get project name from current project
                project_name = Path(self.project_path).name.replace("Project_", "")
                workbench_dir = Path(self.project_path) / "2_workbench"
                
                # Create configuration file
                config_manager = WorkbenchConfigurationManager()
                config_file_path = config_manager.create_project_configuration(str(workbench_dir), project_name)
                
                if config_file_path:
                    print("✅ Workbench configuration created successfully!")
                    print(f"📁 Created: {Path(config_file_path).name}")
                else:
                    print("❌ Failed to create configuration file. Check logs for details.")
            else:
                print("❌ Operation cancelled")
                
        except Exception as e:
            print(f"❌ Error creating configuration: {str(e)}")
        
        input("Press Enter to continue...")
    
    def _list_artifacts_with_upstream(self):
        """List all artifacts with upstream relationships."""
        print("\n📋 Artifacts with Upstream Relations")
        print("-" * 40)
        
        try:
            artifacts = self.workbench_manager.get_artifacts_with_upstream()
            
            if not artifacts:
                print("❌ No artifacts with upstream relationships found")
            else:
                print(f"Found {len(artifacts)} artifacts with upstream relationships:\n")
                
                # Group by stage for better organization
                stages = {}
                for artifact in artifacts:
                    stage = artifact['Stage Name']
                    if stage not in stages:
                        stages[stage] = []
                    stages[stage].append(artifact)
                
                for stage, stage_artifacts in stages.items():
                    print(f"🏗️  {stage} Stage:")
                    for artifact in stage_artifacts:
                        print(f"   • {artifact['Artifact Name']} (ID: {artifact['Artifact ID']})")
                        print(f"     Upstream Relation: {artifact['Upstream Relation']}")
                    print()
                    
        except Exception as e:
            print(f"❌ Error listing artifacts: {str(e)}")
        
        input("Press Enter to continue...")
    
    def _handle_sync_validate(self):
        """Handle sync and validate operations."""
        print("\n🔍 Sync & Validate")
        print("-" * 20)
        print("🚧 Sync & validate operations coming soon!")
        input("Press Enter to continue...")
    
    def _handle_save_workbook(self):
        """Handle saving the workbook."""
        print("\n💾 Save Workbook")
        print("-" * 17)
        print("✅ Workbook saved automatically with each operation")
        input("Press Enter to continue...")
                
# ANCHOR: Main Application Entry Point
if __name__ == "__main__":
    console = ConsoleInterface()
    console.run()
