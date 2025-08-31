"""
File Utilities
==============

Common file and directory operations.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

class FileUtils:
    """File and directory utility functions."""
    
    @staticmethod
    def create_directory_structure(base_path: str, folders: list) -> bool:
        """
        Create directory structure.
        
        Args:
            base_path: Base directory path
            folders: List of folder names to create
            
        Returns:
            bool: True if all directories created successfully
        """
        try:
            for folder in folders:
                folder_path = os.path.join(base_path, folder)
                os.makedirs(folder_path, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error creating directory structure: {str(e)}")
            return False
    
    @staticmethod
    def copy_template_files(source: str, destination: str) -> bool:
        """
        Copy template files to project.
        
        Args:
            source: Source directory containing templates
            destination: Destination directory
            
        Returns:
            bool: True if copy successful
        """
        try:
            if not os.path.exists(source):
                return True  # No templates to copy, which is okay
                
            os.makedirs(destination, exist_ok=True)
            
            for item in os.listdir(source):
                source_path = os.path.join(source, item)
                dest_path = os.path.join(destination, item)
                
                if os.path.isfile(source_path):
                    shutil.copy2(source_path, dest_path)
                elif os.path.isdir(source_path):
                    shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
                    
            return True
            
        except Exception as e:
            print(f"Error copying template files: {str(e)}")
            return False
    
    @staticmethod
    def backup_file(file_path: str) -> str:
        """
        Create backup of file.
        
        Args:
            file_path: Path to file to backup
            
        Returns:
            str: Path to backup file, or empty string if failed
        """
        try:
            if not os.path.exists(file_path):
                return ""
                
            # Create backup filename with timestamp
            file_name = Path(file_path).name
            file_dir = Path(file_path).parent
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{Path(file_name).stem}_{timestamp}{Path(file_name).suffix}"
            backup_path = file_dir / backup_name
            
            shutil.copy2(file_path, str(backup_path))
            return str(backup_path)
            
        except Exception as e:
            print(f"Error creating backup: {str(e)}")
            return ""
    
    @staticmethod
    def ensure_directory_exists(directory_path: str) -> bool:
        """
        Ensure directory exists, create if it doesn't.
        
        Args:
            directory_path: Path to directory
            
        Returns:
            bool: True if directory exists or was created
        """
        try:
            os.makedirs(directory_path, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error ensuring directory exists: {str(e)}")
            return False
