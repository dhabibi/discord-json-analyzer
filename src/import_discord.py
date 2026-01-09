"""Discord JSON import module with batch processing."""

import logging
from pathlib import Path
from typing import List, Dict, Any
from tqdm import tqdm
from .parser import DiscordParser
from .cleaner import DataCleaner
from .config import config

logger = logging.getLogger(__name__)


class DiscordImporter:
    """Import and process Discord JSON export files."""
    
    def __init__(self):
        """Initialize the importer."""
        self.parser = DiscordParser()
        self.cleaner = DataCleaner()
        self.import_results: List[Dict[str, Any]] = []
    
    def import_directory(self, directory: Path = None) -> Dict[str, Any]:
        """Import all JSON files from a directory.
        
        Args:
            directory: Directory path (defaults to config.input_dir)
            
        Returns:
            Dictionary with import statistics
        """
        if directory is None:
            directory = config.input_dir
        
        # Find all JSON files
        json_files = list(directory.glob('*.json'))
        
        if not json_files:
            logger.warning(f"No JSON files found in {directory}")
            return {
                'files_processed': 0,
                'total_messages': 0,
                'total_channels': 0,
                'total_users': 0,
                'errors': []
            }
        
        logger.info(f"Found {len(json_files)} JSON files to process")
        
        # Process each file
        errors = []
        for file_path in tqdm(json_files, desc="Importing JSON files"):
            try:
                result = self.parser.parse_file(file_path)
                self.import_results.append(result)
            except Exception as e:
                error_msg = f"Error processing {file_path.name}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        # Get parsed data
        parsed_data = self.parser.get_parsed_data()
        
        # Clean and validate data
        logger.info("Cleaning and validating data...")
        
        cleaned_messages = self.cleaner.clean_messages(parsed_data['messages'])
        cleaned_users = self.cleaner.clean_users(parsed_data['users'])
        
        valid_messages, validation_errors = self.cleaner.validate_messages(cleaned_messages)
        errors.extend(validation_errors)
        
        # Normalize timestamps
        valid_messages = self.cleaner.normalize_timestamps(
            valid_messages, 
            ['timestamp', 'edited_timestamp']
        )
        
        cleaned_users = self.cleaner.normalize_timestamps(
            cleaned_users,
            ['first_seen', 'last_seen']
        )
        
        # Update parsed data with cleaned data
        parsed_data['messages'] = valid_messages
        parsed_data['users'] = cleaned_users
        
        stats = {
            'files_processed': len(json_files),
            'files_succeeded': len(self.import_results),
            'total_messages': len(valid_messages),
            'total_channels': len(parsed_data['channels']),
            'total_users': len(cleaned_users),
            'errors': errors
        }
        
        logger.info(f"Import complete: {stats}")
        
        return stats
    
    def import_files(self, file_paths: List[Path]) -> Dict[str, Any]:
        """Import specific JSON files.
        
        Args:
            file_paths: List of file paths to import
            
        Returns:
            Dictionary with import statistics
        """
        logger.info(f"Importing {len(file_paths)} specified files")
        
        errors = []
        for file_path in tqdm(file_paths, desc="Importing JSON files"):
            try:
                result = self.parser.parse_file(file_path)
                self.import_results.append(result)
            except Exception as e:
                error_msg = f"Error processing {file_path.name}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        # Get and clean data
        parsed_data = self.parser.get_parsed_data()
        
        cleaned_messages = self.cleaner.clean_messages(parsed_data['messages'])
        cleaned_users = self.cleaner.clean_users(parsed_data['users'])
        
        valid_messages, validation_errors = self.cleaner.validate_messages(cleaned_messages)
        errors.extend(validation_errors)
        
        # Update parsed data
        parsed_data['messages'] = valid_messages
        parsed_data['users'] = cleaned_users
        
        stats = {
            'files_processed': len(file_paths),
            'files_succeeded': len(self.import_results),
            'total_messages': len(valid_messages),
            'total_channels': len(parsed_data['channels']),
            'total_users': len(cleaned_users),
            'errors': errors
        }
        
        return stats
    
    def get_parsed_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get the parsed data.
        
        Returns:
            Dictionary with channels, users, and messages
        """
        return self.parser.get_parsed_data()
    
    def get_import_results(self) -> List[Dict[str, Any]]:
        """Get detailed import results.
        
        Returns:
            List of import result dictionaries
        """
        return self.import_results
    
    def clear(self) -> None:
        """Clear all import data."""
        self.parser.clear()
        self.cleaner.clear()
        self.import_results.clear()
