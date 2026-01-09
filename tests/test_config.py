"""Unit tests for the configuration module."""

import unittest
import os
from pathlib import Path
from src.config import Config


class TestConfig(unittest.TestCase):
    """Test cases for Config class."""
    
    def test_initialization(self):
        """Test config initialization."""
        config = Config()
        
        # Check default values exist
        self.assertIsInstance(config.input_dir, Path)
        self.assertIsInstance(config.output_dir, Path)
        self.assertIsInstance(config.processed_dir, Path)
        self.assertIsInstance(config.batch_size, int)
        self.assertGreater(config.batch_size, 0)
        self.assertIsInstance(config.ai_tools, list)
    
    def test_directories_created(self):
        """Test that directories are created."""
        config = Config()
        
        # Directories should exist after initialization
        self.assertTrue(config.input_dir.exists())
        self.assertTrue(config.output_dir.exists())
        self.assertTrue(config.processed_dir.exists())
    
    def test_batch_size_validation(self):
        """Test batch size is positive."""
        config = Config()
        self.assertGreater(config.batch_size, 0)
    
    def test_ai_tools_list(self):
        """Test AI tools list is populated."""
        config = Config()
        self.assertIsInstance(config.ai_tools, list)
        self.assertGreater(len(config.ai_tools), 0)
    
    def test_log_level_conversion(self):
        """Test log level conversion."""
        config = Config()
        log_level = config.get_log_level()
        
        # Should return a valid logging level
        self.assertIsInstance(log_level, int)
        self.assertIn(log_level, [10, 20, 30, 40, 50])  # DEBUG, INFO, WARNING, ERROR, CRITICAL


if __name__ == '__main__':
    unittest.main()
