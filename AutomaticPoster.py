import os
import logging
from dotenv import load_dotenv
from linkedin_menu import LinkedInAPI
from linkedin_article_generator import ArticleGenerator

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.getenv('LOG_FILE', 'automatic_poster.log')
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class AutomaticPoster:
    """Handles single post generation and posting."""
    def __init__(self):
        self.linkedin_client = LinkedInAPI(os.getenv('LINKEDIN_ACCESS_TOKEN'))
        self.article_generator = ArticleGenerator(os.getenv('GOOGLE_API_KEY'))

    def generate_and_post(self):
        """Generate and post a single piece of content."""
        try:
            # Generate viral topic
            topic = self.article_generator.generate_viral_topic()
            logger.info(f"Generated topic: {topic}")
            print(f"\nGenerated topic: {topic}")
            
            # Generate article
            article = self.article_generator.generate_article(topic)
            logger.info("Generated content")
            print("\nGenerated article:")
            print(article)
            
            # Post to LinkedIn
            response = self.linkedin_client.submit_share(text=article)
            logger.info(f"Post created successfully! Post ID: {response['updateKey']}")
            print(f"\nPost created successfully! Post ID: {response['updateKey']}")
            
        except Exception as e:
            logger.error(f"Error in posting: {str(e)}")
            print(f"\nError creating post: {str(e)}")

def main():
    poster = AutomaticPoster()
    poster.generate_and_post()

if __name__ == "__main__":
    main() 