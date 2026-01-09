"""Unit tests for the cleaner module."""

import unittest
from datetime import datetime
from src.cleaner import DataCleaner


class TestDataCleaner(unittest.TestCase):
    """Test cases for DataCleaner class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.cleaner = DataCleaner()
    
    def test_initialization(self):
        """Test cleaner initialization."""
        self.assertEqual(len(self.cleaner.seen_messages), 0)
        self.assertEqual(len(self.cleaner.seen_users), 0)
    
    def test_extract_urls(self):
        """Test URL extraction."""
        content = "Check out https://example.com and http://test.org for more info"
        urls = self.cleaner.extract_urls(content)
        
        self.assertEqual(len(urls), 2)
        self.assertIn('https://example.com', urls)
        self.assertIn('http://test.org', urls)
    
    def test_extract_domains(self):
        """Test domain extraction from URLs."""
        urls = ['https://example.com/page', 'http://test.org/article']
        domains = self.cleaner.extract_domains(urls)
        
        self.assertEqual(len(domains), 2)
        self.assertIn('example.com', domains)
        self.assertIn('test.org', domains)
    
    def test_contains_code(self):
        """Test code block detection."""
        # With code block
        content1 = "Here's some code: ```python\nprint('hello')\n```"
        self.assertTrue(self.cleaner.contains_code(content1))
        
        # With inline code
        content2 = "Use `print()` function"
        self.assertTrue(self.cleaner.contains_code(content2))
        
        # Without code
        content3 = "Just plain text"
        self.assertFalse(self.cleaner.contains_code(content3))
    
    def test_count_words(self):
        """Test word counting."""
        content = "This is a test message"
        count = self.cleaner.count_words(content)
        self.assertEqual(count, 5)
        
        # Empty content
        self.assertEqual(self.cleaner.count_words(""), 0)
        self.assertEqual(self.cleaner.count_words(None), 0)
    
    def test_clean_messages_deduplication(self):
        """Test message deduplication."""
        messages = [
            {'message_id': 1, 'content': 'Test 1'},
            {'message_id': 2, 'content': 'Test 2'},
            {'message_id': 1, 'content': 'Test 1 duplicate'},  # Duplicate
        ]
        
        cleaned = self.cleaner.clean_messages(messages)
        
        self.assertEqual(len(cleaned), 2)
        self.assertEqual(cleaned[0]['message_id'], 1)
        self.assertEqual(cleaned[1]['message_id'], 2)
    
    def test_validate_messages(self):
        """Test message validation."""
        messages = [
            {'message_id': 1, 'channel_id': 1, 'timestamp': '2024-01-01T12:00:00Z'},
            {'message_id': 2, 'channel_id': 1},  # Missing timestamp
            {'channel_id': 1, 'timestamp': '2024-01-01T12:00:00Z'},  # Missing message_id
        ]
        
        valid, errors = self.cleaner.validate_messages(messages)
        
        self.assertEqual(len(valid), 1)
        self.assertEqual(len(errors), 2)
    
    def test_clean_users_merge_timestamps(self):
        """Test user cleaning with timestamp merging."""
        users = [
            {
                'user_id': 1,
                'username': 'user1',
                'first_seen': '2024-01-01T12:00:00Z',
                'last_seen': '2024-01-01T13:00:00Z'
            },
            {
                'user_id': 1,
                'username': 'user1',
                'first_seen': '2024-01-01T11:00:00Z',  # Earlier
                'last_seen': '2024-01-01T14:00:00Z'   # Later
            }
        ]
        
        cleaned = self.cleaner.clean_users(users)
        
        self.assertEqual(len(cleaned), 1)
        # Should have earliest first_seen and latest last_seen
        user = cleaned[0]
        self.assertIn('2024-01-01T11:00:00', user['first_seen'])
        self.assertIn('2024-01-01T14:00:00', user['last_seen'])
    
    def test_clear(self):
        """Test clearing cleaner data."""
        self.cleaner.seen_messages.add(1)
        self.cleaner.seen_users.add(1)
        
        self.cleaner.clear()
        
        self.assertEqual(len(self.cleaner.seen_messages), 0)
        self.assertEqual(len(self.cleaner.seen_users), 0)


if __name__ == '__main__':
    unittest.main()
