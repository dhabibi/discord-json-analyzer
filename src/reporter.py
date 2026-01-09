"""Report generation module for analytics and insights."""

import json
import csv
import logging
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
from .config import config

logger = logging.getLogger(__name__)


class Reporter:
    """Generate reports and analytics outputs."""
    
    def __init__(self):
        """Initialize the reporter."""
        self.output_dir = config.output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_statistical_summary(self, 
                                    import_stats: Dict[str, Any],
                                    tool_stats: Dict[str, Any],
                                    db_stats: Dict[str, Any] = None) -> Path:
        """Generate statistical summary report.
        
        Args:
            import_stats: Import statistics
            tool_stats: AI tool statistics
            db_stats: Database statistics (optional)
            
        Returns:
            Path to the generated report
        """
        logger.info("Generating statistical summary report")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'statistical_summary_{timestamp}.json'
        output_path = self.output_dir / filename
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'import_statistics': import_stats,
            'ai_tool_statistics': tool_stats,
            'database_statistics': db_stats or {}
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Statistical summary saved to {output_path}")
        return output_path
    
    def generate_ai_tools_report(self, 
                                tool_stats: Dict[str, Any],
                                temporal_trends: Dict[str, Any]) -> Path:
        """Generate AI tools usage report.
        
        Args:
            tool_stats: Tool statistics
            temporal_trends: Temporal trends data
            
        Returns:
            Path to the generated report
        """
        logger.info("Generating AI tools usage report")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'ai_tools_report_{timestamp}.json'
        output_path = self.output_dir / filename
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_mentions': tool_stats.get('total_mentions', 0),
                'unique_tools': tool_stats.get('unique_tools', 0)
            },
            'top_tools': tool_stats.get('top_tools', []),
            'tool_counts': tool_stats.get('tool_counts', {}),
            'mention_type_distribution': tool_stats.get('mention_type_counts', {}),
            'temporal_trends': temporal_trends
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"AI tools report saved to {output_path}")
        return output_path
    
    def generate_resources_report(self, resources: Dict[str, Any]) -> Path:
        """Generate resources and links report.
        
        Args:
            resources: Resources data
            
        Returns:
            Path to the generated report
        """
        logger.info("Generating resources report")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'resources_report_{timestamp}.json'
        output_path = self.output_dir / filename
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_urls': resources.get('total_urls', 0),
                'unique_urls': resources.get('unique_urls', 0)
            },
            'top_urls': resources.get('top_urls', []),
            'top_domains': resources.get('top_domains', []),
            'categorized_resources': resources.get('categorized', {})
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Resources report saved to {output_path}")
        return output_path
    
    def generate_channel_report(self, channel_activity: List[Dict[str, Any]]) -> Path:
        """Generate channel activity report as CSV.
        
        Args:
            channel_activity: Channel activity data
            
        Returns:
            Path to the generated report
        """
        logger.info("Generating channel activity report")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'channel_activity_{timestamp}.csv'
        output_path = self.output_dir / filename
        
        if not channel_activity:
            logger.warning("No channel activity data to report")
            return output_path
        
        # Write CSV
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['channel_id', 'channel_name', 'channel_type', 
                         'message_count', 'unique_users', 'first_message', 'last_message']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            writer.writeheader()
            for row in channel_activity:
                writer.writerow({k: row.get(k, '') for k in fieldnames})
        
        logger.info(f"Channel activity report saved to {output_path}")
        return output_path
    
    def generate_user_report(self, user_activity: List[Dict[str, Any]]) -> Path:
        """Generate user activity report as CSV.
        
        Args:
            user_activity: User activity data
            
        Returns:
            Path to the generated report
        """
        logger.info("Generating user activity report")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'user_activity_{timestamp}.csv'
        output_path = self.output_dir / filename
        
        if not user_activity:
            logger.warning("No user activity data to report")
            return output_path
        
        # Write CSV
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['user_id', 'username', 'display_name', 'is_bot',
                         'message_count', 'first_message', 'last_message']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            writer.writeheader()
            for row in user_activity:
                writer.writerow({k: row.get(k, '') for k in fieldnames})
        
        logger.info(f"User activity report saved to {output_path}")
        return output_path
    
    def generate_insights_dashboard(self,
                                   tool_stats: Dict[str, Any],
                                   temporal_trends: Dict[str, Any],
                                   resources: Dict[str, Any]) -> Path:
        """Generate insights dashboard data for visualization.
        
        Args:
            tool_stats: Tool statistics
            temporal_trends: Temporal trends
            resources: Resources data
            
        Returns:
            Path to the generated dashboard data
        """
        logger.info("Generating insights dashboard data")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'insights_dashboard_{timestamp}.json'
        output_path = self.output_dir / filename
        
        dashboard = {
            'generated_at': datetime.now().isoformat(),
            'tool_statistics': tool_stats,
            'temporal_trends': temporal_trends,
            'resources': resources,
            'visualization_config': {
                'time_series_enabled': True,
                'category_breakdown_enabled': True,
                'top_tools_chart_enabled': True,
                'resource_categories_enabled': True
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(dashboard, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Dashboard data saved to {output_path}")
        return output_path
    
    def generate_executive_summary(self,
                                  import_stats: Dict[str, Any],
                                  tool_stats: Dict[str, Any],
                                  resources: Dict[str, Any]) -> Path:
        """Generate executive summary as text.
        
        Args:
            import_stats: Import statistics
            tool_stats: Tool statistics
            resources: Resources data
            
        Returns:
            Path to the generated summary
        """
        logger.info("Generating executive summary")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'executive_summary_{timestamp}.txt'
        output_path = self.output_dir / filename
        
        # Build summary text
        summary_lines = [
            "=" * 80,
            "DISCORD AI DISCUSSIONS - EXECUTIVE SUMMARY",
            "=" * 80,
            f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "\n" + "=" * 80,
            "\n1. DATA OVERVIEW",
            "-" * 80,
            f"Total messages analyzed: {import_stats.get('total_messages', 0):,}",
            f"Channels processed: {import_stats.get('total_channels', 0)}",
            f"Unique users: {import_stats.get('total_users', 0):,}",
            f"Files processed: {import_stats.get('files_processed', 0)}",
        ]
        
        # AI Tools Section
        top_tools = tool_stats.get('top_tools', [])[:10]
        summary_lines.extend([
            "\n" + "=" * 80,
            "\n2. TOP AI TOOLS MENTIONED",
            "-" * 80,
        ])
        
        for i, tool in enumerate(top_tools, 1):
            summary_lines.append(f"{i:2d}. {tool['name']:30s} - {tool['count']:,} mentions")
        
        # Resources Section
        summary_lines.extend([
            "\n" + "=" * 80,
            "\n3. RESOURCES SHARED",
            "-" * 80,
            f"Total URLs shared: {resources.get('total_urls', 0):,}",
            f"Unique URLs: {resources.get('unique_urls', 0):,}",
        ])
        
        top_domains = resources.get('top_domains', [])[:10]
        if top_domains:
            summary_lines.append("\nTop Domains:")
            for i, domain in enumerate(top_domains, 1):
                summary_lines.append(f"{i:2d}. {domain['domain']:40s} - {domain['count']:,} links")
        
        # Key Insights
        summary_lines.extend([
            "\n" + "=" * 80,
            "\n4. KEY INSIGHTS",
            "-" * 80,
        ])
        
        total_mentions = tool_stats.get('total_mentions', 0)
        unique_tools = tool_stats.get('unique_tools', 0)
        
        if total_mentions > 0:
            summary_lines.append(f"• {total_mentions:,} total AI tool/platform mentions detected")
            summary_lines.append(f"• {unique_tools} different AI tools/platforms discussed")
        
        if top_tools:
            summary_lines.append(f"• Most popular tool: {top_tools[0]['name']} ({top_tools[0]['count']} mentions)")
        
        categorized = resources.get('categorized', {})
        github_count = len(categorized.get('github', []))
        if github_count > 0:
            summary_lines.append(f"• {github_count} GitHub repositories shared")
        
        summary_lines.extend([
            "\n" + "=" * 80,
            "\n5. RECOMMENDATIONS",
            "-" * 80,
            "• Review the detailed AI tools report for temporal trends",
            "• Explore the resources report for valuable learning materials",
            "• Check channel activity report to identify most engaged communities",
            "• Use the dashboard data for interactive visualizations",
            "\n" + "=" * 80,
        ])
        
        # Write summary
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(summary_lines))
        
        logger.info(f"Executive summary saved to {output_path}")
        return output_path
    
    def list_generated_reports(self) -> List[Path]:
        """List all generated reports.
        
        Returns:
            List of report file paths
        """
        reports = list(self.output_dir.glob('*'))
        return sorted(reports, key=lambda p: p.stat().st_mtime, reverse=True)
