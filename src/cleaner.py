"""Data cleaning and validation module."""

import re
import logging
from typing import List, Dict, Any, Set, Tuple
from urllib.parse import urlparse
from datetime import datetime

logger = logging.getLogger(__name__)


class DataCleaner:
    """Data cleaning and validation for Discord messages."""
    
    def __init__(self):
        """Initialize the data cleaner."""
        self.seen_messages: Set[int] = set()
        self.seen_users: Set[int] = set()
        self.url_pattern = re.compile(r'https?://[^\s]+')
        self.mention_pattern = re.compile(r'<@!?(\d+)>')
        self.emoji_pattern = re.compile(r'<a?:[a-zA-Z0-9_]+:\d+>')
        self.code_block_pattern = re.compile(r'```[\s\S]*?```|`[^`]+`')
    
    def clean_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean and deduplicate messages.
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            List of cleaned and deduplicated messages
        """
        cleaned = []
        duplicates = 0
        
        for msg in messages:
            message_id = msg.get('message_id')
            
            # Skip duplicates
            if message_id in self.seen_messages:
                duplicates += 1
                continue
            
            # Clean the message content
            if msg.get('content'):
                msg['content'] = self._clean_content(msg['content'])
            
            self.seen_messages.add(message_id)
            cleaned.append(msg)
        
        logger.info(f"Cleaned {len(cleaned)} messages, removed {duplicates} duplicates")
        return cleaned
    
    def clean_users(self, users: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean and deduplicate users, merging timestamps.
        
        Args:
            users: List of user dictionaries
            
        Returns:
            List of cleaned and deduplicated users
        """
        user_map: Dict[int, Dict[str, Any]] = {}
        
        for user in users:
            user_id = user.get('user_id')
            
            if user_id in user_map:
                # Merge timestamps - keep earliest first_seen and latest last_seen
                existing = user_map[user_id]
                
                first_seen_new = self._parse_iso_timestamp(user.get('first_seen'))
                first_seen_existing = self._parse_iso_timestamp(existing.get('first_seen'))
                
                last_seen_new = self._parse_iso_timestamp(user.get('last_seen'))
                last_seen_existing = self._parse_iso_timestamp(existing.get('last_seen'))
                
                if first_seen_new and first_seen_existing:
                    existing['first_seen'] = min(first_seen_new, first_seen_existing).isoformat()
                
                if last_seen_new and last_seen_existing:
                    existing['last_seen'] = max(last_seen_new, last_seen_existing).isoformat()
            else:
                user_map[user_id] = user
        
        cleaned = list(user_map.values())
        logger.info(f"Cleaned {len(cleaned)} unique users from {len(users)} total")
        return cleaned
    
    def validate_messages(self, messages: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Validate message data.
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Tuple of (valid messages, error messages)
        """
        valid = []
        errors = []
        
        for msg in messages:
            # Check required fields
            if not msg.get('message_id'):
                errors.append("Message missing message_id")
                continue
            
            if not msg.get('channel_id'):
                errors.append(f"Message {msg['message_id']} missing channel_id")
                continue
            
            if not msg.get('timestamp'):
                errors.append(f"Message {msg['message_id']} missing timestamp")
                continue
            
            valid.append(msg)
        
        if errors:
            logger.warning(f"Validation found {len(errors)} invalid messages")
            for error in errors[:10]:  # Log first 10 errors
                logger.warning(error)
        
        return valid, errors
    
    def _clean_content(self, content: str) -> str:
        """Clean message content.
        
        Args:
            content: Raw message content
            
        Returns:
            Cleaned content
        """
        if not content:
            return ""
        
        # Normalize whitespace
        content = ' '.join(content.split())
        
        return content
    
    def extract_urls(self, content: str) -> List[str]:
        """Extract URLs from message content.
        
        Args:
            content: Message content
            
        Returns:
            List of URLs
        """
        if not content:
            return []
        
        urls = self.url_pattern.findall(content)
        return [url.rstrip('.,;:)>') for url in urls]
    
    def extract_domains(self, urls: List[str]) -> List[str]:
        """Extract domains from URLs.
        
        Args:
            urls: List of URLs
            
        Returns:
            List of domains
        """
        domains = []
        for url in urls:
            try:
                parsed = urlparse(url)
                if parsed.netloc:
                    domains.append(parsed.netloc)
            except Exception as e:
                logger.debug(f"Error parsing URL {url}: {e}")
        
        return domains
    
    def contains_code(self, content: str) -> bool:
        """Check if content contains code blocks.
        
        Args:
            content: Message content
            
        Returns:
            True if contains code
        """
        if not content:
            return False
        
        return bool(self.code_block_pattern.search(content))
    
    def extract_mentions(self, content: str) -> List[int]:
        """Extract user mentions from content.
        
        Args:
            content: Message content
            
        Returns:
            List of mentioned user IDs
        """
        if not content:
            return []
        
        matches = self.mention_pattern.findall(content)
        return [int(user_id) for user_id in matches]
    
    def count_words(self, content: str) -> int:
        """Count words in content.
        
        Args:
            content: Message content
            
        Returns:
            Word count
        """
        if not content:
            return 0
        
        # Remove code blocks and URLs for accurate word count
        text = self.code_block_pattern.sub('', content)
        text = self.url_pattern.sub('', text)
        
        words = text.split()
        return len(words)
    
    def _parse_iso_timestamp(self, timestamp: Any) -> datetime:
        """Parse ISO timestamp string.
        
        Args:
            timestamp: Timestamp string or datetime
            
        Returns:
            Datetime object
        """
        if isinstance(timestamp, datetime):
            return timestamp
        
        if isinstance(timestamp, str):
            try:
                return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except Exception as e:
                logger.debug(f"Error parsing timestamp: {e}")
                return datetime.utcnow()
        
        return datetime.utcnow()
    
    def normalize_timestamps(self, items: List[Dict[str, Any]], 
                           timestamp_fields: List[str]) -> List[Dict[str, Any]]:
        """Normalize timestamps to UTC ISO format.
        
        Args:
            items: List of dictionaries with timestamp fields
            timestamp_fields: List of field names to normalize
            
        Returns:
            Items with normalized timestamps
        """
        for item in items:
            for field in timestamp_fields:
                if field in item and item[field]:
                    dt = self._parse_iso_timestamp(item[field])
                    item[field] = dt.isoformat()
        
        return items
    
    def clear(self) -> None:
        """Clear all cached data."""
        self.seen_messages.clear()
        self.seen_users.clear()
