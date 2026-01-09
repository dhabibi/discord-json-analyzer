-- Discord JSON Analyzer - Supabase Database Schema

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS pg_trgm; -- For full-text search

-- Channels table
CREATE TABLE IF NOT EXISTS channels (
    channel_id BIGINT PRIMARY KEY,
    channel_name TEXT NOT NULL,
    channel_type TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Users table
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    username TEXT NOT NULL,
    discriminator TEXT,
    display_name TEXT,
    is_bot BOOLEAN DEFAULT FALSE,
    first_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Messages table
CREATE TABLE IF NOT EXISTS messages (
    message_id BIGINT PRIMARY KEY,
    channel_id BIGINT REFERENCES channels(channel_id) ON DELETE CASCADE,
    user_id BIGINT REFERENCES users(user_id) ON DELETE SET NULL,
    content TEXT,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    edited_timestamp TIMESTAMP WITH TIME ZONE,
    message_type TEXT DEFAULT 'default',
    has_attachments BOOLEAN DEFAULT FALSE,
    has_embeds BOOLEAN DEFAULT FALSE,
    reaction_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- AI mentions table
CREATE TABLE IF NOT EXISTS ai_mentions (
    id SERIAL PRIMARY KEY,
    message_id BIGINT REFERENCES messages(message_id) ON DELETE CASCADE,
    ai_tool_name TEXT NOT NULL,
    mention_type TEXT CHECK (mention_type IN ('tool', 'model', 'platform', 'technique')),
    context_snippet TEXT,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Message analytics table
CREATE TABLE IF NOT EXISTS message_analytics (
    id SERIAL PRIMARY KEY,
    message_id BIGINT UNIQUE REFERENCES messages(message_id) ON DELETE CASCADE,
    word_count INTEGER DEFAULT 0,
    sentiment_score FLOAT,
    contains_code BOOLEAN DEFAULT FALSE,
    contains_links BOOLEAN DEFAULT FALSE,
    extracted_urls JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance

-- Messages table indexes
CREATE INDEX IF NOT EXISTS idx_messages_channel_id ON messages(channel_id);
CREATE INDEX IF NOT EXISTS idx_messages_user_id ON messages(user_id);
CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp);
CREATE INDEX IF NOT EXISTS idx_messages_content_trgm ON messages USING gin (content gin_trgm_ops);

-- AI mentions table indexes
CREATE INDEX IF NOT EXISTS idx_ai_mentions_message_id ON ai_mentions(message_id);
CREATE INDEX IF NOT EXISTS idx_ai_mentions_tool_name ON ai_mentions(ai_tool_name);
CREATE INDEX IF NOT EXISTS idx_ai_mentions_timestamp ON ai_mentions(timestamp);
CREATE INDEX IF NOT EXISTS idx_ai_mentions_type ON ai_mentions(mention_type);

-- Message analytics table indexes
CREATE INDEX IF NOT EXISTS idx_message_analytics_message_id ON message_analytics(message_id);
CREATE INDEX IF NOT EXISTS idx_message_analytics_contains_code ON message_analytics(contains_code) WHERE contains_code = TRUE;
CREATE INDEX IF NOT EXISTS idx_message_analytics_contains_links ON message_analytics(contains_links) WHERE contains_links = TRUE;

-- Users table indexes
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_last_seen ON users(last_seen);

-- Channels table indexes
CREATE INDEX IF NOT EXISTS idx_channels_name ON channels(channel_name);

-- Create views for common queries

-- Most mentioned AI tools view
CREATE OR REPLACE VIEW v_top_ai_tools AS
SELECT 
    ai_tool_name,
    mention_type,
    COUNT(*) as mention_count,
    COUNT(DISTINCT message_id) as unique_messages,
    MIN(timestamp) as first_mention,
    MAX(timestamp) as last_mention
FROM ai_mentions
GROUP BY ai_tool_name, mention_type
ORDER BY mention_count DESC;

-- User activity summary view
CREATE OR REPLACE VIEW v_user_activity AS
SELECT 
    u.user_id,
    u.username,
    u.display_name,
    u.is_bot,
    COUNT(m.message_id) as message_count,
    MIN(m.timestamp) as first_message,
    MAX(m.timestamp) as last_message
FROM users u
LEFT JOIN messages m ON u.user_id = m.user_id
GROUP BY u.user_id, u.username, u.display_name, u.is_bot
ORDER BY message_count DESC;

-- Channel activity summary view
CREATE OR REPLACE VIEW v_channel_activity AS
SELECT 
    c.channel_id,
    c.channel_name,
    c.channel_type,
    COUNT(m.message_id) as message_count,
    COUNT(DISTINCT m.user_id) as unique_users,
    MIN(m.timestamp) as first_message,
    MAX(m.timestamp) as last_message
FROM channels c
LEFT JOIN messages m ON c.channel_id = m.channel_id
GROUP BY c.channel_id, c.channel_name, c.channel_type
ORDER BY message_count DESC;

-- Daily message volume view
CREATE OR REPLACE VIEW v_daily_message_volume AS
SELECT 
    DATE(timestamp) as date,
    COUNT(*) as message_count,
    COUNT(DISTINCT user_id) as active_users,
    COUNT(DISTINCT channel_id) as active_channels
FROM messages
GROUP BY DATE(timestamp)
ORDER BY date DESC;

-- Comments
COMMENT ON TABLE channels IS 'Stores Discord channel information';
COMMENT ON TABLE users IS 'Stores Discord user information';
COMMENT ON TABLE messages IS 'Stores Discord message content and metadata';
COMMENT ON TABLE ai_mentions IS 'Tracks mentions of AI tools, models, and platforms in messages';
COMMENT ON TABLE message_analytics IS 'Stores analyzed metrics for each message';

COMMENT ON VIEW v_top_ai_tools IS 'Ranking of most mentioned AI tools';
COMMENT ON VIEW v_user_activity IS 'Summary of user activity and engagement';
COMMENT ON VIEW v_channel_activity IS 'Summary of channel activity';
COMMENT ON VIEW v_daily_message_volume IS 'Daily message volume statistics';
