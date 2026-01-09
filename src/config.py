"""Configuration management for Discord JSON Analyzer."""

import os
import logging
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration class for application settings."""
    
    def __init__(self):
        """Initialize configuration from environment variables."""
        # Supabase Configuration
        self.supabase_url: str = os.getenv('SUPABASE_URL', '')
        self.supabase_key: str = os.getenv('SUPABASE_KEY', '')
        
        # Directory Configuration
        self.input_dir: Path = Path(os.getenv('INPUT_DIR', './data/raw'))
        self.output_dir: Path = Path(os.getenv('OUTPUT_DIR', './data/reports'))
        self.processed_dir: Path = Path(os.getenv('PROCESSED_DIR', './data/processed'))
        
        # Database Configuration
        self.batch_size: int = int(os.getenv('BATCH_SIZE', '1000'))
        self.connection_pool_size: int = int(os.getenv('CONNECTION_POOL_SIZE', '10'))
        
        # Analysis Configuration
        ai_tools_str = os.getenv('AI_TOOLS', 'ChatGPT,Claude,GPT-4,GPT-3,Midjourney')
        self.ai_tools: List[str] = [tool.strip() for tool in ai_tools_str.split(',')]
        
        # Logging Configuration
        self.log_level: str = os.getenv('LOG_LEVEL', 'INFO')
        self.log_file: str = os.getenv('LOG_FILE', 'discord_analyzer.log')
        
        # Validate configuration
        self._validate()
        
        # Ensure directories exist
        self._create_directories()
    
    def _validate(self) -> None:
        """Validate configuration values."""
        if not self.supabase_url:
            logging.warning("SUPABASE_URL not set in environment variables")
        if not self.supabase_key:
            logging.warning("SUPABASE_KEY not set in environment variables")
        
        if self.batch_size < 1:
            raise ValueError("BATCH_SIZE must be greater than 0")
        
        if self.connection_pool_size < 1:
            raise ValueError("CONNECTION_POOL_SIZE must be greater than 0")
    
    def _create_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
    
    def get_log_level(self) -> int:
        """Convert log level string to logging level constant."""
        levels = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        return levels.get(self.log_level.upper(), logging.INFO)


def setup_logging(config: Config) -> None:
    """Setup logging configuration.
    
    Args:
        config: Configuration object
    """
    logging.basicConfig(
        level=config.get_log_level(),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.log_file),
            logging.StreamHandler()
        ]
    )


# Global config instance
config = Config()
