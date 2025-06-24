"""
Configuration management for DeepTechFinder Patent Analytics.
"""

import os
import yaml
from dataclasses import dataclass
from typing import Dict, Any
from pathlib import Path

@dataclass
class AppConfig:
    name: str
    version: str
    description: str

@dataclass 
class DataConfig:
    input_file: str
    encoding: str
    output_dir: str

@dataclass
class EPOOPSConfig:
    base_url: str
    auth_url: str
    rate_limit_seconds: int
    timeout_seconds: int
    credentials_file: str

@dataclass
class AnalysisConfig:
    default_patent_limit: int
    max_patent_limit: int
    min_patent_limit: int

@dataclass
class ExportConfig:
    csv_format: bool
    pdf_reports: bool
    json_export: bool
    filename_sanitization: bool

@dataclass
class LoggingConfig:
    level: str
    format: str
    file: str

class Config:
    """Main configuration class that loads and manages all settings."""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            # Default to config/settings.yaml relative to project root
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config" / "settings.yaml"
        
        self._load_config(config_path)
    
    def _load_config(self, config_path: Path):
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
            
            self.app = AppConfig(**config_data['app'])
            self.data = DataConfig(**config_data['data'])
            self.epo_ops = EPOOPSConfig(**config_data['epo_ops'])
            self.analysis = AnalysisConfig(**config_data['analysis'])
            self.export = ExportConfig(**config_data['export'])
            self.logging = LoggingConfig(**config_data['logging'])
            
        except Exception as e:
            raise RuntimeError(f"Failed to load configuration from {config_path}: {e}")
    
    def get_project_root(self) -> Path:
        """Get the project root directory."""
        return Path(__file__).parent.parent.parent
    
    def get_data_file_path(self) -> Path:
        """Get full path to the input data file."""
        return self.get_project_root() / self.data.input_file
    
    def get_output_dir_path(self) -> Path:
        """Get full path to the output directory."""
        return self.get_project_root() / self.data.output_dir
    
    def get_credentials_path(self) -> Path:
        """Get full path to EPO OPS credentials file."""
        return self.get_project_root() / self.epo_ops.credentials_file

# Global configuration instance
config = Config()