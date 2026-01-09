#!/usr/bin/env python3
"""
Discord JSON Analyzer - Main Entry Point

A comprehensive tool for importing, analyzing, and storing Discord JSON exports
in Supabase, with AI-focused insights extraction and reporting.
"""

import argparse
import logging
import sys
from pathlib import Path

from src import (
    config,
    setup_logging,
    Database,
    DiscordImporter,
    AIAnalyzer,
    Reporter
)

logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='Import and analyze Discord JSON exports',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Import all JSON files from the default input directory
  python main.py --import
  
  # Import specific files
  python main.py --import --files data/raw/channel1.json data/raw/channel2.json
  
  # Import and analyze
  python main.py --import --analyze
  
  # Generate reports from existing database
  python main.py --report
  
  # Full pipeline: import, analyze, and report
  python main.py --import --analyze --report
  
  # Skip database operations (useful for testing parsing)
  python main.py --import --no-database
        """
    )
    
    parser.add_argument(
        '--import',
        action='store_true',
        dest='do_import',
        help='Import JSON files'
    )
    
    parser.add_argument(
        '--files',
        nargs='+',
        type=Path,
        help='Specific JSON files to import (default: all files in input directory)'
    )
    
    parser.add_argument(
        '--analyze',
        action='store_true',
        help='Analyze messages for AI insights'
    )
    
    parser.add_argument(
        '--report',
        action='store_true',
        help='Generate reports'
    )
    
    parser.add_argument(
        '--no-database',
        action='store_true',
        help='Skip database operations (parsing only)'
    )
    
    parser.add_argument(
        '--input-dir',
        type=Path,
        help=f'Input directory for JSON files (default: {config.input_dir})'
    )
    
    parser.add_argument(
        '--output-dir',
        type=Path,
        help=f'Output directory for reports (default: {config.output_dir})'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default=config.log_level,
        help='Logging level'
    )
    
    return parser.parse_args()


def main():
    """Main execution function."""
    args = parse_arguments()
    
    # Update config if provided
    if args.input_dir:
        config.input_dir = args.input_dir
    if args.output_dir:
        config.output_dir = args.output_dir
    if args.log_level:
        config.log_level = args.log_level
    
    # Setup logging
    setup_logging(config)
    
    logger.info("=" * 80)
    logger.info("Discord JSON Analyzer - Starting")
    logger.info("=" * 80)
    
    # Initialize components
    importer = DiscordImporter()
    analyzer = AIAnalyzer()
    reporter = Reporter()
    db = None
    
    if not args.no_database:
        try:
            db = Database()
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            logger.warning("Continuing without database...")
            db = None
    
    # Import phase
    import_stats = None
    if args.do_import:
        logger.info("\n" + "=" * 80)
        logger.info("PHASE 1: IMPORTING JSON FILES")
        logger.info("=" * 80)
        
        try:
            if args.files:
                import_stats = importer.import_files(args.files)
            else:
                import_stats = importer.import_directory()
            
            logger.info(f"\nImport Summary:")
            logger.info(f"  Files processed: {import_stats['files_processed']}")
            logger.info(f"  Messages imported: {import_stats['total_messages']}")
            logger.info(f"  Channels: {import_stats['total_channels']}")
            logger.info(f"  Users: {import_stats['total_users']}")
            
            if import_stats.get('errors'):
                logger.warning(f"  Errors encountered: {len(import_stats['errors'])}")
            
            # Store in database if available
            if db and import_stats['total_messages'] > 0:
                logger.info("\nStoring data in Supabase...")
                
                parsed_data = importer.get_parsed_data()
                
                # Insert channels
                db.upsert_channels(parsed_data['channels'])
                
                # Insert users
                db.upsert_users(parsed_data['users'])
                
                # Insert messages
                db.upsert_messages(parsed_data['messages'])
                
                logger.info("Data successfully stored in database")
        
        except Exception as e:
            logger.error(f"Error during import: {e}", exc_info=True)
            sys.exit(1)
    
    # Analysis phase
    analysis_results = None
    if args.analyze:
        logger.info("\n" + "=" * 80)
        logger.info("PHASE 2: ANALYZING AI INSIGHTS")
        logger.info("=" * 80)
        
        try:
            if not args.do_import:
                logger.warning("Analysis requested without import. Using data from database...")
                # In a real scenario, you would fetch from database here
                logger.error("Cannot analyze without import in this version. Use --import --analyze")
                sys.exit(1)
            
            parsed_data = importer.get_parsed_data()
            messages = parsed_data['messages']
            
            logger.info(f"Analyzing {len(messages)} messages...")
            analysis_results = analyzer.analyze_messages(messages)
            
            ai_mentions = analysis_results['ai_mentions']
            message_analytics = analysis_results['message_analytics']
            
            logger.info(f"\nAnalysis Summary:")
            logger.info(f"  AI mentions found: {len(ai_mentions)}")
            logger.info(f"  Messages analyzed: {len(message_analytics)}")
            
            # Store analysis results in database
            if db and ai_mentions:
                logger.info("\nStoring analysis results in database...")
                db.insert_ai_mentions(ai_mentions)
                db.upsert_message_analytics(message_analytics)
                logger.info("Analysis results stored in database")
        
        except Exception as e:
            logger.error(f"Error during analysis: {e}", exc_info=True)
            sys.exit(1)
    
    # Reporting phase
    if args.report:
        logger.info("\n" + "=" * 80)
        logger.info("PHASE 3: GENERATING REPORTS")
        logger.info("=" * 80)
        
        try:
            if analysis_results:
                # Generate reports from analysis
                tool_stats = analyzer.generate_tool_statistics(analysis_results['ai_mentions'])
                temporal_trends = analyzer.analyze_temporal_trends(analysis_results['ai_mentions'])
                resources = analyzer.extract_resources(analysis_results['message_analytics'])
                
                # Generate all reports
                stat_report = reporter.generate_statistical_summary(import_stats, tool_stats)
                tools_report = reporter.generate_ai_tools_report(tool_stats, temporal_trends)
                resources_report = reporter.generate_resources_report(resources)
                dashboard = reporter.generate_insights_dashboard(tool_stats, temporal_trends, resources)
                summary = reporter.generate_executive_summary(import_stats, tool_stats, resources)
                
                logger.info(f"\nReports generated:")
                logger.info(f"  Statistical Summary: {stat_report}")
                logger.info(f"  AI Tools Report: {tools_report}")
                logger.info(f"  Resources Report: {resources_report}")
                logger.info(f"  Dashboard Data: {dashboard}")
                logger.info(f"  Executive Summary: {summary}")
                
                # Generate activity reports from database if available
                if db:
                    channel_activity = db.get_channel_activity()
                    user_activity = db.get_user_activity()
                    
                    if channel_activity:
                        channel_report = reporter.generate_channel_report(channel_activity)
                        logger.info(f"  Channel Activity: {channel_report}")
                    
                    if user_activity:
                        user_report = reporter.generate_user_report(user_activity)
                        logger.info(f"  User Activity: {user_report}")
            
            elif db:
                # Generate reports from database
                logger.info("Fetching data from database for reports...")
                
                channel_activity = db.get_channel_activity()
                user_activity = db.get_user_activity()
                top_tools = db.get_top_ai_tools()
                
                if channel_activity:
                    channel_report = reporter.generate_channel_report(channel_activity)
                    logger.info(f"  Channel Activity: {channel_report}")
                
                if user_activity:
                    user_report = reporter.generate_user_report(user_activity)
                    logger.info(f"  User Activity: {user_report}")
                
                if top_tools:
                    logger.info(f"\nTop AI Tools from database:")
                    for i, tool in enumerate(top_tools[:10], 1):
                        logger.info(f"  {i}. {tool.get('ai_tool_name')}: {tool.get('mention_count')} mentions")
            
            else:
                logger.error("Cannot generate reports: no analysis results and no database connection")
                sys.exit(1)
        
        except Exception as e:
            logger.error(f"Error generating reports: {e}", exc_info=True)
            sys.exit(1)
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("Discord JSON Analyzer - Complete")
    logger.info("=" * 80)
    
    if not (args.do_import or args.analyze or args.report):
        logger.warning("No action specified. Use --import, --analyze, or --report")
        logger.info("Run 'python main.py --help' for usage information")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)
