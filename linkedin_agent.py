import os
import json
import time
import schedule
import logging
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai
import requests
import random

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.getenv('LOG_FILE', 'linkedin_automation.log')
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class LinkedInAPI:
    """
    LinkedIn API wrapper for handling authentication and API requests.
    
    This class provides methods to interact with LinkedIn's v2 API,
    focusing on content posting and user information retrieval.
    """
    def __init__(self, access_token):
        """
        Initialize the LinkedIn API client.
        
        Args:
            access_token (str): OAuth2 access token for LinkedIn API
        """
        self.access_token = access_token
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        self.api_url = 'https://api.linkedin.com/v2'
        self.rate_limit_remaining = 100
        self.rate_limit_reset = time.time()

    def _handle_rate_limits(self, response):
        """Handle API rate limits based on response headers."""
        self.rate_limit_remaining = int(response.headers.get('X-RateLimit-Remaining', 100))
        self.rate_limit_reset = int(response.headers.get('X-RateLimit-Reset', time.time()))
        
        if self.rate_limit_remaining <= 0:
            sleep_time = max(0, self.rate_limit_reset - time.time())
            if sleep_time > 0:
                logger.warning(f"Rate limit reached. Sleeping for {sleep_time} seconds")
                time.sleep(sleep_time)

    def _make_request(self, method, endpoint, data=None):
        """
        Make an API request with rate limit handling and error checking.
        
        Args:
            method (str): HTTP method (GET, POST, etc.)
            endpoint (str): API endpoint
            data (dict, optional): Request payload
            
        Returns:
            dict: Response data
            
        Raises:
            Exception: If the API request fails
        """
        url = f"{self.api_url}/{endpoint.lstrip('/')}"
        try:
            response = requests.request(method, url, headers=self.headers, json=data)
            self._handle_rate_limits(response)
            
            if response.status_code == 401:
                raise Exception("Invalid or expired access token")
            elif response.status_code == 403:
                raise Exception("Insufficient permissions or rate limit exceeded")
            elif response.status_code >= 400:
                raise Exception(f"API request failed: {response.text}")
                
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise

    def validate_token(self):
        """
        Validate the access token by making a test API call.
        
        Returns:
            bool: True if token is valid, False otherwise
        """
        try:
            self.get_user_id()
            return True
        except Exception:
            return False

    def submit_share(self, text, title=None, description=None, submitted_url=None, submitted_image_url=None):
        """
        Create a post on LinkedIn with optional media attachments.
        
        Args:
            text (str): The main text content of the post
            title (str, optional): Title for the post when sharing a URL
            description (str, optional): Description for the post when sharing a URL
            submitted_url (str, optional): URL to be shared in the post
            submitted_image_url (str, optional): URL of an image to be shared
            
        Returns:
            dict: Response containing the post ID
            
        Raises:
            Exception: If the post creation fails
        """
        post_data = {
            "author": f"urn:li:person:{self.get_user_id()}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }

        # Add URL sharing if provided
        if submitted_url:
            post_data["specificContent"]["com.linkedin.ugc.ShareContent"].update({
                "shareMediaCategory": "ARTICLE",
                "media": [{
                    "status": "READY",
                    "originalUrl": submitted_url,
                    **({"title": title} if title else {}),
                    **({"description": description} if description else {})
                }]
            })
        # Add image sharing if provided
        elif submitted_image_url:
            post_data["specificContent"]["com.linkedin.ugc.ShareContent"].update({
                "shareMediaCategory": "IMAGE",
                "media": [{
                    "status": "READY",
                    "media": submitted_image_url,
                    "title": {"text": title} if title else {"text": ""}
                }]
            })

        response = self._make_request('POST', 'ugcPosts', post_data)
        if response.status_code == 201:
            return {"updateKey": response.headers.get('x-restli-id')}
        else:
            logger.error(f"Failed to create post: {response.text}")
            raise Exception(f"Failed to create post: {response.status_code}")

    def get_user_id(self):
        """
        Get the current user's LinkedIn ID.
        
        Returns:
            str: LinkedIn member ID
            
        Raises:
            Exception: If unable to retrieve the user ID
        """
        response = self._make_request('GET', 'me')
        if response.status_code == 200:
            return response.json().get('id')
        else:
            logger.error(f"Failed to get user ID: {response.text}")
            raise Exception(f"Failed to get user ID: {response.status_code}")

class LinkedInAutomationAgent:
    def __init__(self):
        # Initialize LinkedIn API client
        self.linkedin_client = LinkedInAPI(os.getenv('LINKEDIN_ACCESS_TOKEN'))
        
        # Initialize Gemini API
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        self.gemini_model = genai.GenerativeModel('gemini-pro')
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize modules
        self._initialize_modules()
        
        # Set up schedules
        self._setup_schedules()
        
        logger.info("LinkedIn Automation Agent initialized successfully")

    def _load_config(self):
        """Load configuration from environment variables and validate values"""
        try:
            config = {
                'posting_schedule': os.getenv('POSTING_SCHEDULE', '09:00,12:00,15:00').split(','),
                'daily_connection_limit': int(os.getenv('DAILY_CONNECTION_LIMIT', 20)),
                'engagement_interval': int(os.getenv('ENGAGEMENT_INTERVAL', 180)),
                'content_tone': os.getenv('CONTENT_TONE', 'professional'),
                'content_length': os.getenv('CONTENT_LENGTH', 'medium'),
                'content_topics': os.getenv('CONTENT_TOPICS', 'AI,Technology,Business').split(','),
                'min_delay': int(os.getenv('MIN_DELAY_BETWEEN_ACTIONS', 60)),
                'max_delay': int(os.getenv('MAX_DELAY_BETWEEN_ACTIONS', 180)),
                'max_retries': int(os.getenv('MAX_RETRIES', 3)),
                'retry_delay': int(os.getenv('RETRY_DELAY', 300))
            }
            
            # Validate configuration
            self._validate_config(config)
            return config
        except ValueError as e:
            logger.error(f"Configuration error: {str(e)}")
            raise

    def _validate_config(self, config):
        """Validate configuration values"""
        # Validate time formats
        for time_slot in config['posting_schedule']:
            try:
                datetime.strptime(time_slot, '%H:%M')
            except ValueError:
                raise ValueError(f"Invalid time format in posting schedule: {time_slot}")

        # Validate numeric ranges
        if not 0 <= config['daily_connection_limit'] <= 100:
            raise ValueError("daily_connection_limit must be between 0 and 100")
        
        if not 30 <= config['engagement_interval'] <= 3600:
            raise ValueError("engagement_interval must be between 30 and 3600 seconds")
        
        if not 30 <= config['min_delay'] <= config['max_delay']:
            raise ValueError("min_delay must be between 30 seconds and max_delay")
        
        if not config['content_topics']:
            raise ValueError("At least one content topic must be specified")

    def _initialize_modules(self):
        """Initialize all automation modules"""
        try:
            from modules.content import ContentModule
            from modules.network import NetworkModule
            from modules.engagement import EngagementModule
            from modules.analytics import AnalyticsModule

            self.content_module = ContentModule(self.gemini_model, self.config)
            self.network_module = NetworkModule(self.linkedin_client, self.gemini_model, self.config)
            self.engagement_module = EngagementModule(self.linkedin_client, self.gemini_model, self.config)
            self.analytics_module = AnalyticsModule()

            logger.info("All modules initialized successfully")
        except ImportError as e:
            logger.error(f"Failed to initialize modules: {str(e)}")
            raise

    def _setup_schedules(self):
        """Set up automated schedules based on configuration"""
        # Schedule content posting
        for time_slot in self.config['posting_schedule']:
            schedule.every().day.at(time_slot).do(self.post_content)
            logger.info(f"Scheduled content posting at {time_slot}")

        # Schedule analytics review
        schedule.every().monday.at("09:00").do(self.review_analytics)
        logger.info("Scheduled analytics review for Mondays at 09:00")

    def post_content(self):
        """Generate and post content to LinkedIn with retries"""
        retries = 0
        while retries < self.config['max_retries']:
            try:
                topic = self._select_topic()
                content = self.content_module.generate_post(topic)
                
                # Validate content
                if not content.get('text'):
                    raise ValueError("Generated content is empty")
                
                # Post to LinkedIn
                response = self.linkedin_client.submit_share(
                    text=content['text'],
                    title=content.get('title', ''),
                    description=content.get('description', ''),
                    submitted_url=content.get('url', ''),
                    submitted_image_url=content.get('image_url', '')
                )
                
                # Log success
                self.analytics_module.log_activity("post", response['updateKey'], {
                    'topic': topic,
                    'engagement': 0,
                    'timestamp': datetime.now().isoformat()
                })
                logger.info(f"Successfully posted content on topic: {topic}")
                return
                
            except Exception as e:
                retries += 1
                logger.warning(f"Attempt {retries} failed to post content: {str(e)}")
                if retries < self.config['max_retries']:
                    time.sleep(self.config['retry_delay'])
                else:
                    logger.error("Max retries reached for posting content")
                    raise

    def review_analytics(self):
        """Review performance and adjust strategies"""
        try:
            report = self.analytics_module.generate_weekly_report()
            logger.info("Weekly analytics review completed")
            
            # Adjust strategies based on analytics
            self._adjust_strategies(report)
        except Exception as e:
            logger.error(f"Failed to review analytics: {str(e)}")

    def _select_topic(self):
        """Select content topic based on strategy and previous performance"""
        try:
            # Get performance data for topics
            topic_performance = self.analytics_module.get_topic_performance()
            
            # If we have performance data, use it to weight topic selection
            if topic_performance:
                # Calculate weights based on engagement rates
                weights = [topic_performance.get(topic, 1) for topic in self.config['content_topics']]
                total_weight = sum(weights)
                normalized_weights = [w/total_weight for w in weights]
                
                # Select topic using weighted random choice
                return random.choices(
                    self.config['content_topics'],
                    weights=normalized_weights,
                    k=1
                )[0]
            
            # If no performance data, rotate topics evenly
            return random.choice(self.config['content_topics'])
            
        except Exception as e:
            logger.error(f"Error selecting topic: {str(e)}")
            # Fallback to random selection
            return random.choice(self.config['content_topics'])

    def _get_random_delay(self):
        """Get a random delay between actions"""
        return random.randint(
            self.config['min_delay'],
            self.config['max_delay']
        )

    def _adjust_strategies(self, analytics_report):
        """Adjust automation strategies based on analytics"""
        try:
            # Analyze posting time performance
            best_times = analytics_report.get('best_posting_times', [])
            if best_times:
                # Update posting schedule if significantly different
                current_times = set(self.config['posting_schedule'])
                if len(current_times.symmetric_difference(set(best_times))) > 1:
                    self.config['posting_schedule'] = best_times
                    self._setup_schedules()
                    logger.info(f"Updated posting schedule to: {best_times}")
            
            # Adjust content strategy
            topic_performance = analytics_report.get('topic_performance', {})
            if topic_performance:
                # Remove consistently underperforming topics
                avg_engagement = sum(topic_performance.values()) / len(topic_performance)
                poor_topics = [
                    topic for topic, score in topic_performance.items()
                    if score < avg_engagement * 0.5
                ]
                
                if poor_topics:
                    self.config['content_topics'] = [
                        topic for topic in self.config['content_topics']
                        if topic not in poor_topics
                    ]
                    logger.info(f"Removed underperforming topics: {poor_topics}")
            
            # Adjust connection limits based on acceptance rate
            acceptance_rate = analytics_report.get('connection_acceptance_rate', 0)
            if acceptance_rate < 0.3:  # Less than 30% acceptance
                self.config['daily_connection_limit'] = max(
                    5,
                    self.config['daily_connection_limit'] - 5
                )
                logger.info(f"Reduced daily connection limit to: {self.config['daily_connection_limit']}")
            
        except Exception as e:
            logger.error(f"Error adjusting strategies: {str(e)}")

    def run(self):
        """Run the automation agent with improved error handling"""
        logger.info("LinkedIn Automation Agent started")
        consecutive_errors = 0
        
        while True:
            try:
                schedule.run_pending()
                
                # Reset error counter on successful iteration
                if consecutive_errors > 0:
                    consecutive_errors = 0
                    logger.info("Recovered from previous errors")
                
                time.sleep(60)
                
            except LinkedInAPIError as e:
                consecutive_errors += 1
                logger.error(f"LinkedIn API error: {str(e)}")
                # Exponential backoff for API errors
                sleep_time = min(300 * (2 ** consecutive_errors), 3600)
                time.sleep(sleep_time)
                
            except Exception as e:
                consecutive_errors += 1
                logger.error(f"Unexpected error in main loop: {str(e)}")
                if consecutive_errors >= 5:
                    logger.critical("Too many consecutive errors, stopping agent")
                    raise
                time.sleep(300)

if __name__ == "__main__":
    agent = LinkedInAutomationAgent()
    agent.run() 