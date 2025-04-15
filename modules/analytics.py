import logging
import json
import os
from typing import Dict, Any, List
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

class AnalyticsModule:
    def __init__(self):
        self.analytics_file = "analytics_data.json"
        self._initialize_analytics_file()
        logger.info("Analytics Module initialized")

    def _initialize_analytics_file(self):
        """Initialize the analytics data file if it doesn't exist"""
        if not os.path.exists(self.analytics_file):
            initial_data = {
                "posts": [],
                "connections": [],
                "engagements": [],
                "metrics": {
                    "post_engagement": {},
                    "connection_growth": {},
                    "network_activity": {}
                }
            }
            with open(self.analytics_file, 'w') as f:
                json.dump(initial_data, f)

    def log_activity(self, activity_type: str, activity_id: str, metadata: Dict[str, Any] = None):
        """Log an activity for analytics tracking"""
        try:
            with open(self.analytics_file, 'r') as f:
                data = json.load(f)

            activity = {
                "id": activity_id,
                "type": activity_type,
                "timestamp": datetime.now().isoformat(),
                "metadata": metadata or {}
            }

            if activity_type == "post":
                data["posts"].append(activity)
            elif activity_type == "connection":
                data["connections"].append(activity)
            elif activity_type == "engagement":
                data["engagements"].append(activity)

            with open(self.analytics_file, 'w') as f:
                json.dump(data, f)

            logger.info(f"Logged {activity_type} activity: {activity_id}")
        except Exception as e:
            logger.error(f"Failed to log activity: {str(e)}")
            raise

    def generate_weekly_report(self) -> Dict[str, Any]:
        """Generate a weekly analytics report"""
        try:
            with open(self.analytics_file, 'r') as f:
                data = json.load(f)

            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)

            # Filter activities for the past week
            weekly_posts = [
                post for post in data["posts"]
                if start_date <= datetime.fromisoformat(post["timestamp"]) <= end_date
            ]
            weekly_connections = [
                conn for conn in data["connections"]
                if start_date <= datetime.fromisoformat(conn["timestamp"]) <= end_date
            ]
            weekly_engagements = [
                eng for eng in data["engagements"]
                if start_date <= datetime.fromisoformat(eng["timestamp"]) <= end_date
            ]

            # Calculate metrics
            report = {
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "posts": {
                    "total": len(weekly_posts),
                    "average_engagement": self._calculate_average_engagement(weekly_posts),
                    "top_performing": self._get_top_performing_posts(weekly_posts)
                },
                "connections": {
                    "new": len(weekly_connections),
                    "acceptance_rate": self._calculate_acceptance_rate(weekly_connections)
                },
                "engagements": {
                    "total": len(weekly_engagements),
                    "by_type": self._categorize_engagements(weekly_engagements)
                },
                "recommendations": self._generate_recommendations(
                    weekly_posts, weekly_connections, weekly_engagements
                )
            }

            logger.info("Generated weekly analytics report")
            return report
        except Exception as e:
            logger.error(f"Failed to generate weekly report: {str(e)}")
            raise

    def _calculate_average_engagement(self, posts: List[Dict[str, Any]]) -> float:
        """Calculate average engagement rate for posts"""
        if not posts:
            return 0.0
        
        total_engagement = sum(
            post["metadata"].get("engagement_rate", 0)
            for post in posts
        )
        return total_engagement / len(posts)

    def _get_top_performing_posts(self, posts: List[Dict[str, Any]], limit: int = 3) -> List[Dict[str, Any]]:
        """Get top performing posts based on engagement"""
        return sorted(
            posts,
            key=lambda x: x["metadata"].get("engagement_rate", 0),
            reverse=True
        )[:limit]

    def _calculate_acceptance_rate(self, connections: List[Dict[str, Any]]) -> float:
        """Calculate connection request acceptance rate"""
        if not connections:
            return 0.0
        
        accepted = sum(
            1 for conn in connections
            if conn["metadata"].get("status") == "accepted"
        )
        return accepted / len(connections)

    def _categorize_engagements(self, engagements: List[Dict[str, Any]]) -> Dict[str, int]:
        """Categorize engagements by type"""
        categories = {}
        for eng in engagements:
            eng_type = eng["metadata"].get("type", "unknown")
            categories[eng_type] = categories.get(eng_type, 0) + 1
        return categories

    def _generate_recommendations(
        self,
        posts: List[Dict[str, Any]],
        connections: List[Dict[str, Any]],
        engagements: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations based on analytics"""
        recommendations = []

        # Post frequency recommendation
        if len(posts) < 3:
            recommendations.append("Consider increasing your posting frequency to maintain visibility")
        elif len(posts) > 10:
            recommendations.append("You might be posting too frequently; consider focusing on quality over quantity")

        # Connection growth recommendation
        if len(connections) < 5:
            recommendations.append("Try to increase your connection requests to grow your network")
        elif len(connections) > 30:
            recommendations.append("Consider being more selective with connection requests to maintain quality")

        # Engagement recommendation
        if len(engagements) < 10:
            recommendations.append("Increase engagement with your network by commenting on posts and sharing content")

        return recommendations

    def generate_visual_report(self, report: Dict[str, Any], output_path: str = "analytics_report.png"):
        """Generate a visual representation of the analytics report"""
        try:
            # Create a figure with subplots
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle('LinkedIn Analytics Report', fontsize=16)

            # Post engagement over time
            post_dates = [
                datetime.fromisoformat(post["timestamp"])
                for post in report["posts"]["top_performing"]
            ]
            post_engagement = [
                post["metadata"].get("engagement_rate", 0)
                for post in report["posts"]["top_performing"]
            ]
            axes[0, 0].plot(post_dates, post_engagement, marker='o')
            axes[0, 0].set_title('Top Performing Posts')
            axes[0, 0].set_xlabel('Date')
            axes[0, 0].set_ylabel('Engagement Rate')

            # Connection growth
            connection_dates = [
                datetime.fromisoformat(conn["timestamp"])
                for conn in report["connections"]["new"]
            ]
            connection_counts = list(range(1, len(connection_dates) + 1))
            axes[0, 1].plot(connection_dates, connection_counts, marker='o')
            axes[0, 1].set_title('Connection Growth')
            axes[0, 1].set_xlabel('Date')
            axes[0, 1].set_ylabel('Total Connections')

            # Engagement types
            engagement_types = list(report["engagements"]["by_type"].keys())
            engagement_counts = list(report["engagements"]["by_type"].values())
            axes[1, 0].bar(engagement_types, engagement_counts)
            axes[1, 0].set_title('Engagement Types')
            axes[1, 0].set_xlabel('Type')
            axes[1, 0].set_ylabel('Count')

            # Recommendations
            axes[1, 1].text(0.1, 0.5, '\n'.join(report["recommendations"]),
                          fontsize=10, verticalalignment='center')
            axes[1, 1].set_title('Recommendations')
            axes[1, 1].axis('off')

            plt.tight_layout()
            plt.savefig(output_path)
            logger.info(f"Generated visual report: {output_path}")
        except Exception as e:
            logger.error(f"Failed to generate visual report: {str(e)}")
            raise 