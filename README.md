# Discord JSON Analyzer

A comprehensive Python application for importing, analyzing, and storing Discord JSON export files in Supabase, with a focus on extracting AI-related discussions, insights, and trends.

## Features

- **Batch Import**: Process multiple Discord JSON export files efficiently
- **Data Cleaning**: Automatic deduplication, validation, and normalization
- **AI Insights**: Identify mentions of AI tools, models, and platforms
- **Resource Extraction**: Extract and categorize shared URLs and resources
- **Supabase Integration**: Store structured data in Supabase with optimized schema
- **Comprehensive Reports**: Generate statistical summaries, trend analysis, and executive reports
- **Error Handling**: Robust error handling with detailed logging
- **CLI Interface**: Flexible command-line interface for different workflows

## Project Structure

```
discord-json-analyzer/
├── src/
│   ├── __init__.py           # Package initialization
│   ├── config.py             # Configuration management
│   ├── database.py           # Supabase database operations
│   ├── parser.py             # JSON parsing and extraction
│   ├── cleaner.py            # Data cleaning and validation
│   ├── import_discord.py     # Import module
│   ├── analyzer.py           # AI insights analyzer
│   └── reporter.py           # Report generation
├── data/
│   ├── raw/                  # Raw Discord JSON exports (place your files here)
│   ├── processed/            # Intermediate processed data
│   └── reports/              # Generated reports
├── sql/
│   └── schema.sql            # Supabase database schema
├── tests/
│   └── test_*.py             # Unit tests
├── .env.example              # Example environment variables
├── .gitignore                # Git ignore file
├── requirements.txt          # Python dependencies
├── README.md                 # This file
└── main.py                   # Main entry point
```

## Installation

### Prerequisites

- Python 3.8 or higher
- A Supabase account and project (optional, for database features)

### Setup Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/dhabibi/discord-json-analyzer.git
   cd discord-json-analyzer
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your Supabase credentials:
   ```
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-anon-or-service-key-here
   ```

5. **Set up Supabase database** (if using database features):
   - Go to your Supabase project dashboard
   - Navigate to the SQL Editor
   - Copy and paste the contents of `sql/schema.sql`
   - Execute the SQL to create tables, indexes, and views

## Usage

### Quick Start

Place your Discord JSON export files in the `data/raw/` directory, then run:

```bash
# Full pipeline: import, analyze, and generate reports
python main.py --import --analyze --report
```

### Command Line Options

```bash
# Import JSON files
python main.py --import

# Import specific files
python main.py --import --files data/raw/channel1.json data/raw/channel2.json

# Import and analyze
python main.py --import --analyze

# Generate reports from existing database
python main.py --report

# Skip database operations (parsing only)
python main.py --import --no-database

# Specify custom directories
python main.py --import --input-dir /path/to/json --output-dir /path/to/reports

# Set log level
python main.py --import --analyze --log-level DEBUG
```

### Full Help

```bash
python main.py --help
```

## Configuration

### Environment Variables

Edit `.env` file to configure:

- **SUPABASE_URL**: Your Supabase project URL
- **SUPABASE_KEY**: Your Supabase API key (anon or service key)
- **INPUT_DIR**: Directory containing JSON files (default: `./data/raw`)
- **OUTPUT_DIR**: Directory for generated reports (default: `./data/reports`)
- **BATCH_SIZE**: Number of records per batch insert (default: 1000)
- **AI_TOOLS**: Comma-separated list of AI tools to track
- **LOG_LEVEL**: Logging level (DEBUG, INFO, WARNING, ERROR)

### AI Tools Tracked

By default, the analyzer tracks mentions of:

- ChatGPT, Claude, GPT-4, GPT-3
- Midjourney, Stable Diffusion, DALL-E
- LangChain, LlamaIndex
- Pinecone, Weaviate, ChromaDB
- OpenAI, Anthropic, Hugging Face
- And more...

You can customize this list in the `.env` file.

## Database Schema

The application creates the following tables in Supabase:

- **channels**: Discord channel information
- **users**: Discord user profiles
- **messages**: Message content and metadata
- **ai_mentions**: Tracked AI tool/platform mentions
- **message_analytics**: Analyzed metrics for each message

Several views are also created for common queries:
- `v_top_ai_tools`: Most mentioned AI tools
- `v_user_activity`: User engagement summary
- `v_channel_activity`: Channel activity summary
- `v_daily_message_volume`: Daily message statistics

## Generated Reports

The application generates multiple report types:

1. **Statistical Summary** (JSON): Overall statistics about imported data
2. **AI Tools Report** (JSON): Detailed AI tool mentions and trends
3. **Resources Report** (JSON): Extracted URLs categorized by type
4. **Channel Activity** (CSV): Per-channel activity metrics
5. **User Activity** (CSV): Per-user engagement metrics
6. **Insights Dashboard** (JSON): Data ready for visualization
7. **Executive Summary** (TXT): Human-readable summary of key findings

All reports are saved in the `data/reports/` directory with timestamps.

## Discord JSON Export Format

This tool expects Discord JSON exports in the standard format:

```json
{
  "channel": {
    "id": "123456789",
    "name": "channel-name",
    "type": "text"
  },
  "messages": [
    {
      "id": "987654321",
      "content": "Message text here",
      "timestamp": "2024-01-01T12:00:00.000+00:00",
      "author": {
        "id": "111222333",
        "username": "user123",
        "discriminator": "1234",
        "bot": false
      },
      "attachments": [],
      "embeds": [],
      "reactions": []
    }
  ]
}
```

Or as a simple array of messages:
```json
[
  {
    "id": "987654321",
    "content": "Message text",
    ...
  }
]
```

## Examples

### Example 1: Import and Analyze 29 Channels

```bash
# Place all 29 JSON files in data/raw/
python main.py --import --analyze --report
```

### Example 2: Analyze Without Database

Useful for testing or when you don't have Supabase set up:

```bash
python main.py --import --analyze --report --no-database
```

### Example 3: Update Existing Database

```bash
# Import new data
python main.py --import --analyze

# Later, generate updated reports
python main.py --report
```

## Error Handling

The application includes comprehensive error handling:

- **Malformed JSON**: Files with JSON errors are logged and skipped
- **Missing Fields**: Messages with missing required fields are validated
- **Duplicates**: Automatic deduplication of messages and users
- **Database Errors**: Graceful degradation when database is unavailable
- **Logging**: All operations logged to file and console

Check `discord_analyzer.log` for detailed logs.

## Development

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=src
```

### Code Style

This project follows PEP 8 style guidelines. To check your code:

```bash
# Install development dependencies
pip install flake8 black

# Check style
flake8 src/

# Auto-format
black src/
```

## Troubleshooting

### "No JSON files found"

- Ensure your JSON files are in the `data/raw/` directory
- Or specify a custom directory with `--input-dir`

### "Failed to connect to database"

- Check your `.env` file has correct Supabase credentials
- Verify your Supabase project is active
- Use `--no-database` flag to skip database operations

### "Module not found" errors

- Ensure you've activated your virtual environment
- Run `pip install -r requirements.txt` again

### Import errors with large files

- The tool uses streaming for large files
- Increase batch size in `.env` if needed
- Check available memory

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Acknowledgments

- Built for analyzing AI-related Discord community discussions
- Uses Supabase for scalable data storage
- Inspired by the need to understand AI tool adoption trends

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review the logs in `discord_analyzer.log`

## Roadmap

Future enhancements:

- [ ] Sentiment analysis for AI tool mentions
- [ ] Interactive web dashboard
- [ ] Real-time Discord bot integration
- [ ] Export to other database formats
- [ ] Advanced NLP for topic modeling
- [ ] Machine learning for trend prediction
