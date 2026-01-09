"""Supabase database connection and operations module."""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from supabase import create_client, Client
from .config import config

logger = logging.getLogger(__name__)


class Database:
    """Database handler for Supabase operations."""
    
    def __init__(self):
        """Initialize Supabase client."""
        if not config.supabase_url or not config.supabase_key:
            raise ValueError("Supabase URL and KEY must be provided")
        
        self.client: Client = create_client(config.supabase_url, config.supabase_key)
        logger.info("Supabase client initialized successfully")
    
    def upsert_channels(self, channels: List[Dict[str, Any]]) -> int:
        """Insert or update channels in batch.
        
        Args:
            channels: List of channel dictionaries
            
        Returns:
            Number of channels upserted
        """
        if not channels:
            return 0
        
        try:
            result = self.client.table('channels').upsert(channels).execute()
            logger.info(f"Upserted {len(channels)} channels")
            return len(channels)
        except Exception as e:
            logger.error(f"Error upserting channels: {e}")
            raise
    
    def upsert_users(self, users: List[Dict[str, Any]]) -> int:
        """Insert or update users in batch.
        
        Args:
            users: List of user dictionaries
            
        Returns:
            Number of users upserted
        """
        if not users:
            return 0
        
        try:
            result = self.client.table('users').upsert(users).execute()
            logger.info(f"Upserted {len(users)} users")
            return len(users)
        except Exception as e:
            logger.error(f"Error upserting users: {e}")
            raise
    
    def upsert_messages(self, messages: List[Dict[str, Any]]) -> int:
        """Insert or update messages in batch.
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Number of messages upserted
        """
        if not messages:
            return 0
        
        try:
            # Process in batches
            total = 0
            batch_size = config.batch_size
            
            for i in range(0, len(messages), batch_size):
                batch = messages[i:i + batch_size]
                result = self.client.table('messages').upsert(batch).execute()
                total += len(batch)
                logger.info(f"Upserted batch of {len(batch)} messages (total: {total}/{len(messages)})")
            
            return total
        except Exception as e:
            logger.error(f"Error upserting messages: {e}")
            raise
    
    def insert_ai_mentions(self, mentions: List[Dict[str, Any]]) -> int:
        """Insert AI mentions in batch.
        
        Args:
            mentions: List of AI mention dictionaries
            
        Returns:
            Number of mentions inserted
        """
        if not mentions:
            return 0
        
        try:
            # Process in batches
            total = 0
            batch_size = config.batch_size
            
            for i in range(0, len(mentions), batch_size):
                batch = mentions[i:i + batch_size]
                result = self.client.table('ai_mentions').insert(batch).execute()
                total += len(batch)
                logger.info(f"Inserted batch of {len(batch)} AI mentions (total: {total}/{len(mentions)})")
            
            return total
        except Exception as e:
            logger.error(f"Error inserting AI mentions: {e}")
            raise
    
    def upsert_message_analytics(self, analytics: List[Dict[str, Any]]) -> int:
        """Insert or update message analytics in batch.
        
        Args:
            analytics: List of analytics dictionaries
            
        Returns:
            Number of analytics records upserted
        """
        if not analytics:
            return 0
        
        try:
            # Process in batches
            total = 0
            batch_size = config.batch_size
            
            for i in range(0, len(analytics), batch_size):
                batch = analytics[i:i + batch_size]
                result = self.client.table('message_analytics').upsert(batch).execute()
                total += len(batch)
                logger.info(f"Upserted batch of {len(batch)} analytics (total: {total}/{len(analytics)})")
            
            return total
        except Exception as e:
            logger.error(f"Error upserting message analytics: {e}")
            raise
    
    def get_top_ai_tools(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get top mentioned AI tools.
        
        Args:
            limit: Maximum number of results
            
        Returns:
            List of AI tools with mention counts
        """
        try:
            result = self.client.table('v_top_ai_tools').select('*').limit(limit).execute()
            return result.data
        except Exception as e:
            logger.error(f"Error fetching top AI tools: {e}")
            return []
    
    def get_user_activity(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get user activity summary.
        
        Args:
            limit: Maximum number of results
            
        Returns:
            List of user activity records
        """
        try:
            result = self.client.table('v_user_activity').select('*').limit(limit).execute()
            return result.data
        except Exception as e:
            logger.error(f"Error fetching user activity: {e}")
            return []
    
    def get_channel_activity(self) -> List[Dict[str, Any]]:
        """Get channel activity summary.
        
        Returns:
            List of channel activity records
        """
        try:
            result = self.client.table('v_channel_activity').select('*').execute()
            return result.data
        except Exception as e:
            logger.error(f"Error fetching channel activity: {e}")
            return []
    
    def get_daily_message_volume(self, limit: int = 365) -> List[Dict[str, Any]]:
        """Get daily message volume.
        
        Args:
            limit: Maximum number of days
            
        Returns:
            List of daily volume records
        """
        try:
            result = self.client.table('v_daily_message_volume').select('*').limit(limit).execute()
            return result.data
        except Exception as e:
            logger.error(f"Error fetching daily message volume: {e}")
            return []
    
    def execute_raw_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute a raw SQL query.
        
        Args:
            query: SQL query string
            
        Returns:
            Query results
        """
        try:
            result = self.client.rpc(query).execute()
            return result.data
        except Exception as e:
            logger.error(f"Error executing raw query: {e}")
            return []
