import os
import json
import time
import logging
from dotenv import load_dotenv
import requests
from urllib.parse import urlencode

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
    """LinkedIn API wrapper for handling authentication and API requests."""
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = "https://api.linkedin.com/v2"
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0',
            'LinkedIn-Version': '202304'
        }

    def _make_request(self, method, endpoint, data=None):
        """Make an API request with error handling."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = requests.request(method, url, headers=self.headers, json=data)
            
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

    def get_user_id(self):
        """Get the current user's LinkedIn ID using OpenID Connect."""
        try:
            response = self._make_request('GET', 'userinfo')
            if response.status_code == 200:
                profile_data = response.json()
                user_id = profile_data.get('sub')
                if not user_id:
                    raise Exception("Could not find user ID in profile response")
                return user_id
            else:
                raise Exception(f"Failed to get user ID: {response.text}")
        except Exception as e:
            logger.error(f"Error getting user ID: {str(e)}")
            raise

    def submit_share(self, text, title=None, description=None, url=None):
        """
        Create a share on LinkedIn.
        
        Args:
            text (str): The main text content of the share
            title (str, optional): Title for the share when sharing a URL
            description (str, optional): Description for the share when sharing a URL
            url (str, optional): URL to be shared
            
        Returns:
            dict: Response containing the share ID
        """
        try:
            # Get the author URN
            user_id = self.get_user_id()
            author_urn = f"urn:li:person:{user_id}"
            
            # Prepare the share content
            share_content = {
                "author": author_urn,
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

            # If URL is provided, update the share content for article sharing
            if url:
                share_content["specificContent"]["com.linkedin.ugc.ShareContent"].update({
                    "shareMediaCategory": "ARTICLE",
                    "media": [{
                        "status": "READY",
                        "originalUrl": url,
                        **({"title": {"text": title}} if title else {}),
                        **({"description": {"text": description}} if description else {})
                    }]
                })

            # Log the request body for debugging
            logger.info(f"Creating share with body: {json.dumps(share_content, indent=2)}")

            # Make the API request
            response = self._make_request('POST', 'ugcPosts', share_content)
            
            if response.status_code in [200, 201]:
                share_id = response.headers.get('x-restli-id')
                logger.info(f"Successfully created share with ID: {share_id}")
                return {"updateKey": share_id}
            else:
                raise Exception(f"Failed to create share: {response.text}")
                
        except Exception as e:
            logger.error(f"Error creating share: {str(e)}")
            raise

class ContentGenerator:
    """Handles content generation using Gemini API."""
    def __init__(self, api_key):
        self.api_key = api_key
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        self.tech_topics = [
            "Web Development", "Cloud Computing", "DevOps", "AI/ML", 
            "Cybersecurity", "Blockchain", "Data Science", "Mobile Development",
            "Software Architecture", "Programming Languages", "Database Systems",
            "API Development", "Microservices", "System Design", "Cloud Native"
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
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise

    def generate_topic_options(self, base_topic):
        """Generate 5 interesting topic options based on the base topic."""
        prompt = f"""Generate 5 unique and engaging LinkedIn post topics about {base_topic} in the tech industry.
        Each topic should:
        - Be specific and focused
        - Include a catchy title
        - Be relevant to full-stack developers
        - Be current and trending
        - Include 1-2 relevant emojis
        
        Format the response as a numbered list with each topic on a new line.
        Example:
        1. 🚀 The Future of Web Development: What's Next?
        2. 💡 5 Game-Changing Tools Every Developer Should Know
        
        Return only the numbered list, no additional text."""
        
        response = self._make_request(prompt)
        topics = response['candidates'][0]['content']['parts'][0]['text'].strip().split('\n')
        return [topic.strip() for topic in topics if topic.strip()]

    def generate_content(self, topic):
        """Generate engaging tech-focused content for the post."""
        prompt = f"""Write a LinkedIn post about this topic: {topic}
        The post should:
        - Be under 200 words
        - Start with a hook that grabs attention
        - Include 2-3 relevant emojis
        - Share personal experiences or insights
        - Include practical examples or code snippets
        - End with a thought-provoking question
        - Be written from a full-stack developer's perspective
        - Use plain text only (no markdown or special formatting)
        - Be concise and engaging
        
        Return only the post content with emojis, no additional text."""
        
        response = self._make_request(prompt)
        return response['candidates'][0]['content']['parts'][0]['text'].strip()

def main():
    # Initialize APIs
    linkedin_client = LinkedInAPI(os.getenv('LINKEDIN_ACCESS_TOKEN'))
    content_generator = ContentGenerator(os.getenv('GOOGLE_API_KEY'))

    while True:
        print("\nLinkedIn Tech Content Creator")
        print("1. Create and post tech content")
        print("2. Validate Token")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ")
        
        if choice == "1":
            try:
                # Display available tech topics
                print("\nAvailable Tech Topics:")
                for i, topic in enumerate(content_generator.tech_topics, 1):
                    print(f"{i}. {topic}")
                
                # Get base topic from user
                topic_choice = input("\nEnter the number of your base topic (or type your own): ").strip()
                if topic_choice.isdigit() and 1 <= int(topic_choice) <= len(content_generator.tech_topics):
                    base_topic = content_generator.tech_topics[int(topic_choice) - 1]
                else:
                    base_topic = topic_choice

                if not base_topic:
                    print("Topic cannot be empty. Please try again.")
                    continue

                # Generate topic options
                print("\nGenerating interesting topic options...")
                topic_options = content_generator.generate_topic_options(base_topic)
                
                # Display topic options
                print("\nGenerated Topic Options:")
                for i, topic in enumerate(topic_options, 1):
                    print(f"{i}. {topic}")
                
                # Let user select a topic
                selected_topic = input("\nEnter the number of the topic you want to use (or type your own): ").strip()
                if selected_topic.isdigit() and 1 <= int(selected_topic) <= len(topic_options):
                    final_topic = topic_options[int(selected_topic) - 1]
                else:
                    final_topic = selected_topic

                # Generate content
                print("\nGenerating content...")
                content = content_generator.generate_content(final_topic)
                print(f"\nGenerated content:\n{content}")
                
                # Ask if user wants to include a URL
                include_url = input("\nDo you want to include a URL in your post? (y/n): ").lower()
                url = None
                if include_url == 'y':
                    url = input("Enter the URL to share: ").strip()
                
                # Confirm posting
                confirm = input("\nDo you want to post this content? (y/n): ").lower()
                if confirm == 'y':
                    # Post to LinkedIn
                    response = linkedin_client.submit_share(
                        text=content,
                        url=url
                    )
                    print("\nPost successfully created!")
                    print(f"Post ID: {response['updateKey']}")
                else:
                    print("\nPost cancelled.")
                
            except Exception as e:
                print(f"\nError: {str(e)}")
                logger.error(f"Error in content creation: {str(e)}")
        
        elif choice == "2":
            try:
                if linkedin_client.validate_token():
                    print("\nToken is valid!")
                else:
                    print("\nToken validation failed. Please run linkedin_auth.py to get a new token.")
            except Exception as e:
                print(f"\nError validating token: {str(e)}")
        
        elif choice == "3":
            print("\nGoodbye!")
            break
        
        else:
            print("\nInvalid choice. Please try again.")

if __name__ == "__main__":
    main() 