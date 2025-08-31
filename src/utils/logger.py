"""
Application Logger
=================

Centralized logging for the DWH Creator application.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

class Logger:
    """Application logging manager."""
    
    def __init__(self, log_level: str = "INFO"):
        """Initialize logger with specified level."""
        self.logger = logging.getLogger("DWH_Creator")
        if not self.logger.handlers:  # Avoid duplicate handlers
            self.setup_logging(log_level)
    
    def setup_logging(self, log_level: str):
        """Setup logging configuration."""
        # Set log level
        level = getattr(logging, log_level.upper(), logging.INFO)
        self.logger.setLevel(level)
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(console_handler)
    
    def info(self, message: str):
        """Log info message."""
        self.logger.info(message)
    
    def error(self, message: str):
        """Log error message."""
        self.logger.error(message)
    
    def debug(self, message: str):
        """Log debug message."""
        self.logger.debug(message)
    
    def warning(self, message: str):
        """Log warning message."""
        self.logger.warning(message)
