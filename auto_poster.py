import os
import time
import random
import logging
import requests
from dotenv import load_dotenv
from linkedin_menu import LinkedInAPI

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.getenv('LOG_FILE', 'auto_poster.log')
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class ArticleGenerator:
    """Generates viral tech articles using Gemini API."""
    def __init__(self, api_key):
        self.api_key = api_key
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        
        # Content themes
        self.content_themes = {
            "personal_growth": {
                "emoji": "🔍",
                "topics": [
                    "Lessons from my biggest tech failure",
                    "3 unconventional habits that 2x'd my coding productivity",
                    "How I landed my dream dev role with no CS degree",
                    "The mindset shift that transformed my debugging process",
                    "My journey from imposter syndrome to tech lead"
                ]
            },
            "industry_insights": {
                "emoji": "🚀",
                "topics": [
                    "Why microservices might be killing your startup",
                    "The future of frontend development: My bold predictions",
                    "REST vs GraphQL: Real-world lessons learned",
                    "AI tools in development: Hype vs. Reality",
                    "The hidden costs of over-engineering"
                ]
            },
            "thought_leadership": {
                "emoji": "🧠",
                "topics": [
                    "Unpopular opinion: Code comments are overrated",
                    "Why junior developers should ignore 'best practices'",
                    "The case against daily standups",
                    "Test-driven development is dead. Here's why.",
                    "Why I stopped using the latest frameworks"
                ]
            },
            "tactical_value": {
                "emoji": "🎯",
                "topics": [
                    "How I reduced API response time by 80%",
                    "My VS Code setup that saves 2 hours/week",
                    "5 CLI tools every developer should know",
                    "The git workflow that saved our team",
                    "Docker optimization tricks nobody talks about"
                ]
            },
            "relatable_content": {
                "emoji": "💡",
                "topics": [
                    "What they don't tell you about being a tech lead",
                    "Behind the scenes: Debugging a production crisis",
                    "Real talk: My first month as a senior developer",
                    "The emotional rollercoaster of code reviews",
                    "Confessions of a self-taught developer"
                ]
            }
        }

        # Hook styles
        self.hook_styles = [
            "Curious: 'Ever wondered why {topic}?'",
            "Bold: 'Forget everything you know about {topic}.'",
            "Relatable: 'We've all been there... {topic}'",
            "Contrarian: 'Here's why everyone is wrong about {topic}.'",
            "Story: 'Last week, I made a mistake that taught me everything about {topic}.'",
            "Metric: 'One simple change led to {X}% improvement in {topic}.'",
            "Question: 'Is {topic} actually making you a worse developer?'",
            "Revelation: 'The truth about {topic} nobody talks about:'"
        ]

    def _make_request(self, prompt):
        """Make a request to Gemini API."""
        headers = {
            'Content-Type': 'application/json'
        }
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        try:
            response = requests.post(
                f"{self.api_url}?key={self.api_key}",
                headers=headers,
                json=data
            )
            if response.status_code != 200:
                raise Exception(f"API request failed: {response.text}")
            return response.json()
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            raise

    def generate_viral_topic(self):
        """Generate a viral-worthy tech topic."""
        # Randomly select a theme and topic
        theme_key = random.choice(list(self.content_themes.keys()))
        theme = self.content_themes[theme_key]
        base_topic = random.choice(theme["topics"])
        
        prompt = f"""Generate a viral LinkedIn post title based on this topic: {base_topic}

        Theme: {theme_key.replace('_', ' ').title()} ({theme['emoji']})
        
        Guidelines:
        - Keep the essence of the original topic
        - Add specific numbers or results where relevant
        - Include 1-2 relevant emojis
        - Make it attention-grabbing
        - Keep it under 100 characters
        - Make it specific and credible
        
        Return only the title with emojis, no additional text."""
        
        response = self._make_request(prompt)
        return response['candidates'][0]['content']['parts'][0]['text'].strip()

    def generate_article(self, topic):
        """Generate an engaging article using the AIDA framework."""
        # Select a random hook style
        hook_style = random.choice(self.hook_styles)
        
        prompt = f"""Write a viral LinkedIn post about: {topic}

        Follow this AIDA framework strictly:

        1. ATTENTION (Hook):
        - Use this hook style: {hook_style}
        - Make it impossible to scroll past
        - 2-3 lines maximum

        2. INTEREST:
        - Present the main problem or opportunity
        - Add a surprising fact or statistic
        - Use personal experience
        - 2-3 lines

        3. DESIRE:
        - Share your main insights or solutions
        - Include specific examples or results
        - Add practical takeaways
        - 3-4 lines

        4. ACTION:
        - End with an engaging question
        - Encourage discussion
        - Add 2-3 relevant hashtags
        - 2 lines maximum

        Format Requirements:
        - Total length: 300-800 words
        - Use short paragraphs (2-3 lines max)
        - Add line breaks between sections
        - Use 3-4 relevant emojis strategically
        - Use these bullet markers sparingly: 👉 💡 🔑
        - Make it skimmable
        - Plain text only (no markdown)
        - Write in a personal, conversational tone

        Return only the formatted post text."""
        
        response = self._make_request(prompt)
        return response['candidates'][0]['content']['parts'][0]['text'].strip()

class AutoPoster:
    """Handles automatic posting with random intervals."""
    def __init__(self, linkedin_client, article_generator):
        self.linkedin_client = linkedin_client
        self.article_generator = article_generator
        self.is_running = False
        self.posts_count = 0

    def generate_and_post(self):
        """Generate and post a single piece of content."""
        try:
            # Generate viral topic
            topic = self.article_generator.generate_viral_topic()
            logger.info(f"Generated topic: {topic}")
            
            # Generate article
            article = self.article_generator.generate_article(topic)
            logger.info("Generated content")
            
            # Post to LinkedIn
            response = self.linkedin_client.submit_share(text=article)
            self.posts_count += 1
            logger.info(f"Post #{self.posts_count} created successfully! Post ID: {response['updateKey']}")
            print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Post #{self.posts_count} created!")
            print(f"Topic: {topic}")
            
        except Exception as e:
            logger.error(f"Error in auto-posting: {str(e)}")
            print(f"\nError creating post: {str(e)}")

    def start_auto_posting(self):
        """Start automatic posting with random intervals."""
        self.is_running = True
        print("\nStarting automatic posting mode...")
        print("Press Ctrl+C to stop")
        
        try:
            while self.is_running:
                self.generate_and_post()
                # Random interval between 30 and 180 minutes
                interval = random.randint(30, 180) * 60  # Convert minutes to seconds
                logger.info(f"Waiting {interval//60} minutes until next post...")
                print(f"\nWaiting {interval//60} minutes until next post...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            self.is_running = False
            print("\nStopping automatic posting mode...")
            print(f"Total posts created: {self.posts_count}")

def main():
    # Initialize components
    linkedin_client = LinkedInAPI(os.getenv('LINKEDIN_ACCESS_TOKEN'))
    article_generator = ArticleGenerator(os.getenv('GOOGLE_API_KEY'))
    auto_poster = AutoPoster(linkedin_client, article_generator)
    
    # Start automatic posting
    auto_poster.start_auto_posting()

if __name__ == "__main__":
    main() 