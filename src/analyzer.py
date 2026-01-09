"""AI insights and analysis engine module."""

import re
import logging
from typing import List, Dict, Any, Set, Tuple
from collections import defaultdict, Counter
from datetime import datetime
from .config import config
from .cleaner import DataCleaner

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """Analyzer for extracting AI-related insights from messages."""
    
    def __init__(self):
        """Initialize the analyzer."""
        self.cleaner = DataCleaner()
        
        # AI tool patterns (case-insensitive)
        self.ai_tools = {tool.lower(): tool for tool in config.ai_tools}
        
        # Additional patterns for AI mentions
        self.tool_patterns = self._compile_tool_patterns()
        
        # Categories for AI mentions
        self.tool_categories = {
            'chatgpt': 'tool',
            'claude': 'tool',
            'gpt-4': 'model',
            'gpt-3': 'model',
            'gpt-3.5': 'model',
            'midjourney': 'tool',
            'stable diffusion': 'tool',
            'dall-e': 'tool',
            'dall·e': 'tool',
            'langchain': 'platform',
            'llamaindex': 'platform',
            'pinecone': 'platform',
            'weaviate': 'platform',
            'chromadb': 'platform',
            'openai': 'platform',
            'anthropic': 'platform',
            'hugging face': 'platform',
            'replicate': 'platform',
            'runway': 'tool',
            'cohere': 'platform',
            'ai21': 'platform',
            'vector database': 'technique',
            'embedding': 'technique',
            'fine-tuning': 'technique',
            'prompt engineering': 'technique',
            'rag': 'technique',
            'retrieval augmented generation': 'technique'
        }
    
    def _compile_tool_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for AI tool detection.
        
        Returns:
            Dictionary of tool name to compiled pattern
        """
        patterns = {}
        for tool_key, tool_name in self.ai_tools.items():
            # Create pattern that matches the tool name with word boundaries
            pattern = re.compile(r'\b' + re.escape(tool_key) + r'\b', re.IGNORECASE)
            patterns[tool_name] = pattern
        
        return patterns
    
    def analyze_messages(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze messages for AI-related content.
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Dictionary with analysis results
        """
        logger.info(f"Analyzing {len(messages)} messages for AI insights")
        
        ai_mentions = []
        message_analytics = []
        
        for msg in messages:
            # Extract AI mentions
            mentions = self._extract_ai_mentions(msg)
            ai_mentions.extend(mentions)
            
            # Create message analytics
            analytics = self._create_message_analytics(msg)
            message_analytics.append(analytics)
        
        logger.info(f"Found {len(ai_mentions)} AI mentions")
        
        return {
            'ai_mentions': ai_mentions,
            'message_analytics': message_analytics
        }
    
    def _extract_ai_mentions(self, message: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract AI tool mentions from a message.
        
        Args:
            message: Message dictionary
            
        Returns:
            List of AI mention dictionaries
        """
        content = message.get('content', '')
        if not content:
            return []
        
        mentions = []
        content_lower = content.lower()
        
        # Check for each AI tool
        for tool_name, pattern in self.tool_patterns.items():
            if pattern.search(content):
                # Find context around the mention
                context = self._extract_context(content, tool_name)
                
                # Determine mention type
                tool_key = tool_name.lower()
                mention_type = self.tool_categories.get(tool_key, 'tool')
                
                mention = {
                    'message_id': message['message_id'],
                    'ai_tool_name': tool_name,
                    'mention_type': mention_type,
                    'context_snippet': context,
                    'timestamp': message['timestamp']
                }
                mentions.append(mention)
        
        return mentions
    
    def _extract_context(self, content: str, tool_name: str, 
                        context_size: int = 100) -> str:
        """Extract context around an AI tool mention.
        
        Args:
            content: Message content
            tool_name: Name of the tool
            context_size: Characters of context to extract
            
        Returns:
            Context snippet
        """
        # Find the position of the tool name (case-insensitive)
        content_lower = content.lower()
        tool_lower = tool_name.lower()
        
        pos = content_lower.find(tool_lower)
        if pos == -1:
            return content[:context_size]
        
        # Extract context around the mention
        start = max(0, pos - context_size // 2)
        end = min(len(content), pos + len(tool_name) + context_size // 2)
        
        snippet = content[start:end].strip()
        
        # Add ellipsis if truncated
        if start > 0:
            snippet = '...' + snippet
        if end < len(content):
            snippet = snippet + '...'
        
        return snippet
    
    def _create_message_analytics(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Create analytics record for a message.
        
        Args:
            message: Message dictionary
            
        Returns:
            Analytics dictionary
        """
        content = message.get('content', '')
        
        # Extract URLs
        urls = self.cleaner.extract_urls(content)
        
        # Count words
        word_count = self.cleaner.count_words(content)
        
        # Check for code
        contains_code = self.cleaner.contains_code(content)
        
        # Check for links
        contains_links = len(urls) > 0
        
        analytics = {
            'message_id': message['message_id'],
            'word_count': word_count,
            'sentiment_score': None,  # Placeholder for future sentiment analysis
            'contains_code': contains_code,
            'contains_links': contains_links,
            'extracted_urls': urls if urls else None
        }
        
        return analytics
    
    def generate_tool_statistics(self, ai_mentions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate statistics about AI tool mentions.
        
        Args:
            ai_mentions: List of AI mention dictionaries
            
        Returns:
            Statistics dictionary
        """
        if not ai_mentions:
            return {
                'total_mentions': 0,
                'unique_tools': 0,
                'tool_counts': {},
                'mention_type_counts': {}
            }
        
        # Count mentions by tool
        tool_counts = Counter(m['ai_tool_name'] for m in ai_mentions)
        
        # Count by mention type
        type_counts = Counter(m['mention_type'] for m in ai_mentions)
        
        # Get top tools
        top_tools = tool_counts.most_common(20)
        
        return {
            'total_mentions': len(ai_mentions),
            'unique_tools': len(tool_counts),
            'tool_counts': dict(tool_counts),
            'mention_type_counts': dict(type_counts),
            'top_tools': [{'name': name, 'count': count} for name, count in top_tools]
        }
    
    def analyze_temporal_trends(self, ai_mentions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze temporal trends in AI tool mentions.
        
        Args:
            ai_mentions: List of AI mention dictionaries
            
        Returns:
            Temporal trends dictionary
        """
        if not ai_mentions:
            return {}
        
        # Group mentions by tool and date
        tool_timeline = defaultdict(lambda: defaultdict(int))
        
        for mention in ai_mentions:
            tool = mention['ai_tool_name']
            timestamp = mention['timestamp']
            
            try:
                # Parse timestamp and extract date
                if isinstance(timestamp, str):
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                else:
                    dt = timestamp
                
                date_key = dt.strftime('%Y-%m-%d')
                tool_timeline[tool][date_key] += 1
            except Exception as e:
                logger.debug(f"Error parsing timestamp: {e}")
        
        # Convert to serializable format
        timeline_data = {
            tool: dict(dates) for tool, dates in tool_timeline.items()
        }
        
        return {
            'tool_timeline': timeline_data,
            'date_range': self._get_date_range(ai_mentions)
        }
    
    def _get_date_range(self, ai_mentions: List[Dict[str, Any]]) -> Dict[str, str]:
        """Get date range from mentions.
        
        Args:
            ai_mentions: List of AI mention dictionaries
            
        Returns:
            Dictionary with start and end dates
        """
        if not ai_mentions:
            return {'start': None, 'end': None}
        
        dates = []
        for mention in ai_mentions:
            try:
                timestamp = mention['timestamp']
                if isinstance(timestamp, str):
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                else:
                    dt = timestamp
                dates.append(dt)
            except Exception:
                continue
        
        if not dates:
            return {'start': None, 'end': None}
        
        return {
            'start': min(dates).strftime('%Y-%m-%d'),
            'end': max(dates).strftime('%Y-%m-%d')
        }
    
    def extract_resources(self, message_analytics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract and categorize URLs from messages.
        
        Args:
            message_analytics: List of message analytics
            
        Returns:
            Dictionary of categorized resources
        """
        all_urls = []
        url_counts = Counter()
        domain_counts = Counter()
        
        for analytics in message_analytics:
            urls = analytics.get('extracted_urls')
            if urls:
                all_urls.extend(urls)
                url_counts.update(urls)
                
                # Extract domains
                domains = self.cleaner.extract_domains(urls)
                domain_counts.update(domains)
        
        # Categorize URLs by domain patterns
        categorized = self._categorize_urls(all_urls)
        
        return {
            'total_urls': len(all_urls),
            'unique_urls': len(url_counts),
            'top_urls': [{'url': url, 'count': count} for url, count in url_counts.most_common(20)],
            'top_domains': [{'domain': domain, 'count': count} for domain, count in domain_counts.most_common(20)],
            'categorized': categorized
        }
    
    def _categorize_urls(self, urls: List[str]) -> Dict[str, List[str]]:
        """Categorize URLs by type.
        
        Args:
            urls: List of URLs
            
        Returns:
            Dictionary of categorized URLs
        """
        categories = {
            'github': [],
            'documentation': [],
            'articles': [],
            'videos': [],
            'papers': [],
            'other': []
        }
        
        for url in urls:
            url_lower = url.lower()
            
            if 'github.com' in url_lower:
                categories['github'].append(url)
            elif 'youtube.com' in url_lower or 'youtu.be' in url_lower:
                categories['videos'].append(url)
            elif 'arxiv.org' in url_lower or 'paper' in url_lower:
                categories['papers'].append(url)
            elif any(doc in url_lower for doc in ['docs.', 'documentation', 'readme']):
                categories['documentation'].append(url)
            elif any(ext in url_lower for ext in ['blog', 'article', 'post', 'medium.com']):
                categories['articles'].append(url)
            else:
                categories['other'].append(url)
        
        # Remove duplicates and limit
        for category in categories:
            categories[category] = list(set(categories[category]))[:50]
        
        return categories
