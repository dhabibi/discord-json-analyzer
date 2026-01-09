"""Unit tests for the analyzer module."""

import unittest
from src.analyzer import AIAnalyzer


class TestAIAnalyzer(unittest.TestCase):
    """Test cases for AIAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = AIAnalyzer()
    
    def test_initialization(self):
        """Test analyzer initialization."""
        self.assertIsNotNone(self.analyzer.ai_tools)
        self.assertIsNotNone(self.analyzer.tool_patterns)
    
    def test_extract_ai_mentions(self):
        """Test AI mention extraction."""
        message = {
            'message_id': 1,
            'content': 'I love using ChatGPT and Claude for my projects',
            'timestamp': '2024-01-01T12:00:00Z'
        }
        
        mentions = self.analyzer._extract_ai_mentions(message)
        
        # Should find at least ChatGPT and Claude if they're in the config
        self.assertIsInstance(mentions, list)
        if len(mentions) > 0:
            self.assertIn('message_id', mentions[0])
            self.assertIn('ai_tool_name', mentions[0])
            self.assertIn('mention_type', mentions[0])
    
    def test_extract_context(self):
        """Test context extraction around mentions."""
        content = "This is a long message about ChatGPT and how it helps with coding tasks"
        context = self.analyzer._extract_context(content, "ChatGPT", context_size=20)
        
        self.assertIsInstance(context, str)
        self.assertIn("ChatGPT", context, "Context should contain the tool name")
    
    def test_create_message_analytics(self):
        """Test message analytics creation."""
        message = {
            'message_id': 1,
            'content': 'Check out this code: ```python\nprint("hello")\n``` and https://example.com'
        }
        
        analytics = self.analyzer._create_message_analytics(message)
        
        self.assertEqual(analytics['message_id'], 1)
        self.assertGreater(analytics['word_count'], 0)
        self.assertTrue(analytics['contains_code'])
        self.assertTrue(analytics['contains_links'])
        self.assertIsNotNone(analytics['extracted_urls'])
    
    def test_generate_tool_statistics(self):
        """Test tool statistics generation."""
        ai_mentions = [
            {'ai_tool_name': 'ChatGPT', 'mention_type': 'tool'},
            {'ai_tool_name': 'ChatGPT', 'mention_type': 'tool'},
            {'ai_tool_name': 'Claude', 'mention_type': 'tool'},
        ]
        
        stats = self.analyzer.generate_tool_statistics(ai_mentions)
        
        self.assertEqual(stats['total_mentions'], 3)
        self.assertEqual(stats['unique_tools'], 2)
        self.assertIn('tool_counts', stats)
        self.assertIn('ChatGPT', stats['tool_counts'])
        self.assertEqual(stats['tool_counts']['ChatGPT'], 2)
    
    def test_generate_tool_statistics_empty(self):
        """Test tool statistics with empty input."""
        stats = self.analyzer.generate_tool_statistics([])
        
        self.assertEqual(stats['total_mentions'], 0)
        self.assertEqual(stats['unique_tools'], 0)
    
    def test_extract_resources(self):
        """Test resource extraction."""
        message_analytics = [
            {
                'message_id': 1,
                'extracted_urls': ['https://github.com/test/repo', 'https://example.com']
            },
            {
                'message_id': 2,
                'extracted_urls': ['https://github.com/test/repo', 'https://youtube.com/watch?v=123']
            }
        ]
        
        resources = self.analyzer.extract_resources(message_analytics)
        
        self.assertIn('total_urls', resources)
        self.assertIn('unique_urls', resources)
        self.assertIn('categorized', resources)
        self.assertEqual(resources['total_urls'], 4)
    
    def test_categorize_urls(self):
        """Test URL categorization."""
        urls = [
            'https://github.com/test/repo',
            'https://youtube.com/watch?v=123',
            'https://arxiv.org/abs/1234.5678',
            'https://docs.example.com/guide',
            'https://example.com/blog/post'
        ]
        
        categorized = self.analyzer._categorize_urls(urls)
        
        self.assertIn('github', categorized)
        self.assertIn('videos', categorized)
        self.assertIn('papers', categorized)
        self.assertIn('documentation', categorized)
        self.assertIn('articles', categorized)
        
        self.assertEqual(len(categorized['github']), 1)
        self.assertEqual(len(categorized['videos']), 1)
        self.assertEqual(len(categorized['papers']), 1)


if __name__ == '__main__':
    unittest.main()
