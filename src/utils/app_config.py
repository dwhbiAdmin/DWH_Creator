"""
Application Configuration Manager
=================================

Handles loading and managing application configuration from config files.
Provides secure access to API keys and other settings.
"""

import os
import configparser
from pathlib import Path
from typing import Optional, Dict, Any


class AppConfig:
    """Manages application configuration settings."""
    
    def __init__(self, config_file: str = None):
        """
        Initialize configuration manager.
        
        Args:
            config_file: Path to configuration file (defaults to config/config.ini)
        """
        self.config = configparser.ConfigParser()
        
        # Determine config file path
        if config_file is None:
            # Get the DWH_Creator root directory
            current_file = Path(__file__)
            dwh_creator_root = current_file.parent.parent.parent
            config_file = dwh_creator_root / "config" / "config.ini"
        
        self.config_file = Path(config_file)
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file."""
        try:
            if self.config_file.exists():
                self.config.read(self.config_file)
            else:
                print(f"Warning: Configuration file not found: {self.config_file}")
                # Create a default configuration
                self._create_default_config()
        except Exception as e:
            print(f"Error loading configuration: {e}")
            self._create_default_config()
    
    def _create_default_config(self):
        """Create default configuration if file doesn't exist."""
        self.config.clear()
        
        # Default OpenAI settings
        self.config.add_section('openai')
        self.config.set('openai', 'api_key', '')
        self.config.set('openai', 'model', 'gpt-4')
        
        # Default application settings
        self.config.add_section('application')
        self.config.set('application', 'default_projects_folder', '_DWH_Projects')
        self.config.set('application', 'log_level', 'INFO')
        
        # Default Excel settings
        self.config.add_section('excel')
        self.config.set('excel', 'backup_on_save', 'true')
        self.config.set('excel', 'auto_width_columns', 'true')
        
        # Default template settings
        self.config.add_section('templates')
        self.config.set('templates', 'default_encoding', 'utf-8')
    
    def get_openai_api_key(self) -> Optional[str]:
        """
        Get OpenAI API key from configuration or environment.
        
        Returns:
            str: API key if available, None otherwise
        """
        # First try environment variable
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            return api_key
        
        # Then try config file
        try:
            api_key = self.config.get('openai', 'api_key', fallback='')
            return api_key if api_key else None
        except:
            return None
    
    def get_openai_model(self) -> str:
        """
        Get OpenAI model to use.
        
        Returns:
            str: Model name (defaults to gpt-4)
        """
        try:
            return self.config.get('openai', 'model', fallback='gpt-4')
        except:
            return 'gpt-4'
    
    def get_default_projects_folder(self) -> str:
        """
        Get default projects folder name.
        
        Returns:
            str: Folder name (defaults to _DWH_Projects)
        """
        try:
            return self.config.get('application', 'default_projects_folder', fallback='_DWH_Projects')
        except:
            return '_DWH_Projects'
    
    def get_log_level(self) -> str:
        """
        Get logging level.
        
        Returns:
            str: Log level (defaults to INFO)
        """
        try:
            return self.config.get('application', 'log_level', fallback='INFO')
        except:
            return 'INFO'
    
    def get_excel_backup_on_save(self) -> bool:
        """
        Get whether to backup Excel files on save.
        
        Returns:
            bool: True if backup should be created
        """
        try:
            return self.config.getboolean('excel', 'backup_on_save', fallback=True)
        except:
            return True
    
    def get_excel_auto_width_columns(self) -> bool:
        """
        Get whether to auto-width Excel columns.
        
        Returns:
            bool: True if columns should be auto-sized
        """
        try:
            return self.config.getboolean('excel', 'auto_width_columns', fallback=True)
        except:
            return True
    
    def get_template_encoding(self) -> str:
        """
        Get default template file encoding.
        
        Returns:
            str: Encoding (defaults to utf-8)
        """
        try:
            return self.config.get('templates', 'default_encoding', fallback='utf-8')
        except:
            return 'utf-8'
    
    def save_config(self):
        """Save current configuration to file."""
        try:
            # Ensure config directory exists
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                self.config.write(f)
            return True
        except Exception as e:
            print(f"Error saving configuration: {e}")
            return False
    
    def set_openai_api_key(self, api_key: str):
        """
        Set OpenAI API key in configuration.
        
        Args:
            api_key: The API key to store
        """
        if not self.config.has_section('openai'):
            self.config.add_section('openai')
        self.config.set('openai', 'api_key', api_key)
    
    def get_all_settings(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all configuration settings as a dictionary.
        
        Returns:
            dict: All configuration sections and their settings
        """
        result = {}
        for section_name in self.config.sections():
            result[section_name] = dict(self.config.items(section_name))
        return result
