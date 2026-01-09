"""Unit tests for the parser module."""

import unittest
import json
from pathlib import Path
from datetime import datetime
from src.parser import DiscordParser


class TestDiscordParser(unittest.TestCase):
    """Test cases for DiscordParser class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = DiscordParser()
    
    def test_initialization(self):
        """Test parser initialization."""
        self.assertEqual(len(self.parser.channels), 0)
        self.assertEqual(len(self.parser.users), 0)
        self.assertEqual(len(self.parser.messages), 0)
        self.assertEqual(len(self.parser.user_cache), 0)
    
    def test_parse_timestamp(self):
        """Test timestamp parsing."""
        # ISO format with Z
        ts1 = self.parser._parse_timestamp("2024-01-01T12:00:00.000Z")
        self.assertIsInstance(ts1, datetime)
        
        # ISO format with timezone
        ts2 = self.parser._parse_timestamp("2024-01-01T12:00:00.000+00:00")
        self.assertIsInstance(ts2, datetime)
        
        # None timestamp
        ts3 = self.parser._parse_timestamp(None)
        self.assertIsNone(ts3)
    
    def test_extract_user(self):
        """Test user extraction."""
        author = {
            'id': '123456789',
            'username': 'testuser',
            'discriminator': '1234',
            'bot': False
        }
        
        user = self.parser._extract_user(author, "2024-01-01T12:00:00.000Z")
        
        self.assertEqual(user['user_id'], 123456789)
        self.assertEqual(user['username'], 'testuser')
        self.assertEqual(user['discriminator'], '1234')
        self.assertFalse(user['is_bot'])
    
    def test_extract_message(self):
        """Test message extraction."""
        channel = {
            'channel_id': 111111,
            'channel_name': 'test-channel',
            'channel_type': 'text'
        }
        
        msg_data = {
            'id': '987654321',
            'content': 'Test message',
            'timestamp': '2024-01-01T12:00:00.000Z',
            'author': {
                'id': '123456789',
                'username': 'testuser'
            },
            'attachments': [],
            'embeds': [],
            'reactions': []
        }
        
        message, user = self.parser._extract_message(msg_data, channel)
        
        self.assertIsNotNone(message)
        self.assertIsNotNone(user)
        self.assertEqual(message['message_id'], 987654321)
        self.assertEqual(message['content'], 'Test message')
        self.assertEqual(message['channel_id'], 111111)
    
    def test_clear(self):
        """Test clearing parser data."""
        # Add some data
        self.parser.channels.append({'id': 1})
        self.parser.users.append({'id': 1})
        self.parser.messages.append({'id': 1})
        self.parser.user_cache[1] = {'id': 1}
        
        # Clear
        self.parser.clear()
        
        # Verify cleared
        self.assertEqual(len(self.parser.channels), 0)
        self.assertEqual(len(self.parser.users), 0)
        self.assertEqual(len(self.parser.messages), 0)
        self.assertEqual(len(self.parser.user_cache), 0)


if __name__ == '__main__':
    unittest.main()
