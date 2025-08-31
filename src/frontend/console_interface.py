"""
Console Interface for DWH Creator
=================================

Provides a command-line interface for the DWH Creator application.
Implements the main menu structure and user interaction flow.
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
current_dir = Path(__file__).parent
src_dir = current_dir.parent
sys.path.insert(0, str(src_dir))

from backend.project_manager import ProjectManager
from utils.logger import Logger

class ConsoleInterface:
    """
    Console-based user interface for DWH Creator.
    """
    
    def __init__(self):
        """Initialize the console interface."""
        self.project_manager = ProjectManager()
        self.logger = Logger()
        self.current_project_path = None
        
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
                
                # Ask if user wants to open Excel workbook
                open_excel = input("\n📊 Open Excel workbook now? (y/n): ").strip().lower()
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
                
                # Ask if user wants to open Excel workbook
                open_excel = input("\n📊 Open Excel workbook? (y/n): ").strip().lower()
                if open_excel in ['y', 'yes']:
                    self.project_manager.open_excel_workbook(project_path)
            else:
                print("❌ Failed to open project")
        except Exception as e:
            print(f"❌ Error opening project: {str(e)}")
            
    def show_project_status(self):
        """Show current project status."""
        if self.current_project_path:
            print(f"\n📊 Current Project: {os.path.basename(self.current_project_path)}")
            print(f"📁 Location: {self.current_project_path}")
        else:
            print("\n❌ No project currently open")
            
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
                print("\n🚧 Workbench Operations - Coming soon!")
                input("Press Enter to continue...")
            elif choice == 4 and self.current_project_path:
                print("\n🚧 Generate Artifacts - Coming soon!")
                input("Press Enter to continue...")
            elif choice == 5 and self.current_project_path:
                print("\n🚧 Documentation - Coming soon!")
                input("Press Enter to continue...")
                
if __name__ == "__main__":
    console = ConsoleInterface()
    console.run()
