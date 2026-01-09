"""JSON parsing and data extraction module for Discord exports."""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class DiscordParser:
    """Parser for Discord JSON export files."""
    
    def __init__(self):
        """Initialize the parser."""
        self.channels: List[Dict[str, Any]] = []
        self.users: List[Dict[str, Any]] = []
        self.messages: List[Dict[str, Any]] = []
        self.user_cache: Dict[int, Dict[str, Any]] = {}
    
    def parse_file(self, file_path: Path) -> Dict[str, Any]:
        """Parse a single Discord JSON export file.
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            Dictionary with parsed data counts
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"Parsing file: {file_path.name}")
            
            # Extract channel info
            channel = self._extract_channel(data, file_path)
            if channel:
                self.channels.append(channel)
            
            # Extract messages
            messages = data.get('messages', [])
            if isinstance(data, list):
                # Sometimes the export is just a list of messages
                messages = data
            
            parsed_count = 0
            for msg_data in messages:
                msg, user = self._extract_message(msg_data, channel)
                if msg:
                    self.messages.append(msg)
                    parsed_count += 1
                if user and user['user_id'] not in self.user_cache:
                    self.user_cache[user['user_id']] = user
                    self.users.append(user)
            
            logger.info(f"Parsed {parsed_count} messages from {file_path.name}")
            
            return {
                'file': str(file_path),
                'messages_parsed': parsed_count,
                'channel': channel['channel_name'] if channel else 'unknown'
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error in {file_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
            raise
    
    def _extract_channel(self, data: Dict[str, Any], file_path: Path) -> Optional[Dict[str, Any]]:
        """Extract channel information from JSON data.
        
        Args:
            data: JSON data
            file_path: Original file path
            
        Returns:
            Channel dictionary or None
        """
        # Try to extract channel info from the data
        channel_id = data.get('channel', {}).get('id')
        channel_name = data.get('channel', {}).get('name')
        channel_type = data.get('channel', {}).get('type')
        
        # If not found in data, try to infer from filename
        if not channel_id:
            # Use filename as fallback
            channel_name = file_path.stem
            # Generate a pseudo-ID from the filename
            channel_id = abs(hash(channel_name)) % (10 ** 10)
        
        if not channel_name:
            channel_name = file_path.stem
        
        return {
            'channel_id': int(channel_id) if channel_id else abs(hash(channel_name)) % (10 ** 10),
            'channel_name': str(channel_name),
            'channel_type': str(channel_type) if channel_type else 'text',
            'created_at': datetime.utcnow().isoformat()
        }
    
    def _extract_message(self, msg_data: Dict[str, Any], channel: Optional[Dict[str, Any]]) -> tuple:
        """Extract message and user information.
        
        Args:
            msg_data: Message data from JSON
            channel: Channel information
            
        Returns:
            Tuple of (message dict, user dict)
        """
        try:
            # Extract message ID
            message_id = msg_data.get('id')
            if not message_id:
                return None, None
            
            # Extract user info
            author = msg_data.get('author', {})
            user = self._extract_user(author, msg_data.get('timestamp'))
            
            # Extract message content
            content = msg_data.get('content', '')
            
            # Extract timestamps
            timestamp = self._parse_timestamp(msg_data.get('timestamp'))
            edited_timestamp = self._parse_timestamp(msg_data.get('edited_timestamp'))
            
            # Extract attachments and embeds
            attachments = msg_data.get('attachments', [])
            embeds = msg_data.get('embeds', [])
            
            # Extract reactions
            reactions = msg_data.get('reactions', [])
            reaction_count = sum(r.get('count', 0) for r in reactions)
            
            message = {
                'message_id': int(message_id),
                'channel_id': channel['channel_id'] if channel else 0,
                'user_id': user['user_id'] if user else None,
                'content': content,
                'timestamp': timestamp.isoformat() if timestamp else datetime.utcnow().isoformat(),
                'edited_timestamp': edited_timestamp.isoformat() if edited_timestamp else None,
                'message_type': msg_data.get('type', 'default'),
                'has_attachments': len(attachments) > 0,
                'has_embeds': len(embeds) > 0,
                'reaction_count': reaction_count
            }
            
            return message, user
            
        except Exception as e:
            logger.warning(f"Error extracting message: {e}")
            return None, None
    
    def _extract_user(self, author: Dict[str, Any], timestamp: Optional[str]) -> Optional[Dict[str, Any]]:
        """Extract user information.
        
        Args:
            author: Author data from message
            timestamp: Message timestamp
            
        Returns:
            User dictionary or None
        """
        try:
            user_id = author.get('id')
            if not user_id:
                return None
            
            parsed_time = self._parse_timestamp(timestamp)
            time_iso = parsed_time.isoformat() if parsed_time else datetime.utcnow().isoformat()
            
            return {
                'user_id': int(user_id),
                'username': author.get('username', 'unknown'),
                'discriminator': author.get('discriminator', '0000'),
                'display_name': author.get('global_name') or author.get('username', 'unknown'),
                'is_bot': author.get('bot', False),
                'first_seen': time_iso,
                'last_seen': time_iso
            }
        except Exception as e:
            logger.warning(f"Error extracting user: {e}")
            return None
    
    def _parse_timestamp(self, timestamp: Optional[str]) -> Optional[datetime]:
        """Parse timestamp string to datetime.
        
        Args:
            timestamp: Timestamp string
            
        Returns:
            Datetime object or None
        """
        if not timestamp:
            return None
        
        try:
            # Try ISO format first
            if 'T' in timestamp:
                return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            # Try other common formats
            from dateutil import parser
            return parser.parse(timestamp)
        except Exception as e:
            logger.warning(f"Error parsing timestamp '{timestamp}': {e}")
            return None
    
    def get_parsed_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all parsed data.
        
        Returns:
            Dictionary with channels, users, and messages
        """
        return {
            'channels': self.channels,
            'users': self.users,
            'messages': self.messages
        }
    
    def clear(self) -> None:
        """Clear all parsed data."""
        self.channels.clear()
        self.users.clear()
        self.messages.clear()
        self.user_cache.clear()
