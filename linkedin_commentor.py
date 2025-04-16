import os
import time
import json
import logging
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from linkedin_menu import LinkedInAPI

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.getenv('LOG_FILE', 'linkedin_comments.log')
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class CommentResponder:
    """Handles LinkedIn comment responses using Gemini AI."""
    def __init__(self, linkedin_client, gemini_api_key):
        self.linkedin_client = linkedin_client
        self.gemini_api_key = gemini_api_key
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        self.processed_comments = set()  # Track processed comments to avoid duplicates
        
    def _make_gemini_request(self, prompt):
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
                f"{self.api_url}?key={self.gemini_api_key}",
                headers=headers,
                json=data
            )
            if response.status_code != 200:
                raise Exception(f"API request failed: {response.text}")
            return response.json()
        except Exception as e:
            logger.error(f"Gemini request failed: {str(e)}")
            raise

    def generate_comment_response(self, original_comment, post_content):
        """Generate an insightful response to a comment using Gemini AI."""
        prompt = f"""Generate a professional and insightful LinkedIn comment response.

Original Post Content:
{post_content}

Comment to Respond To:
{original_comment}

Guidelines:
- Keep the response professional and friendly
- Acknowledge the commenter's point
- Add value with additional insights or information
- Keep it concise (2-3 sentences)
- Use 1-2 relevant emojis
- Make it feel personal and engaging
- Avoid generic responses
- If the comment is negative, respond constructively
- If it's a question, provide a helpful answer

Return only the response text with emojis."""
        
        response = self._make_gemini_request(prompt)
        return response['candidates'][0]['content']['parts'][0]['text'].strip()

    def get_recent_posts(self, hours=24):
        """Get recent posts from the last X hours."""
        try:
            # Get user's recent activity
            response = self.linkedin_client._make_request(
                "GET",
                "/v2/ugcPosts",
                params={
                    "q": "author",
                    "author": f"urn:li:person:{self.linkedin_client.get_user_id()}",
                    "count": 10
                }
            )
            posts = response.get('elements', [])
            
            # Filter posts from the last X hours
            recent_posts = []
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            for post in posts:
                created_time = datetime.fromtimestamp(post['created']['time'] / 1000)
                if created_time > cutoff_time:
                    recent_posts.append(post)
            
            return recent_posts
        except Exception as e:
            logger.error(f"Error fetching recent posts: {str(e)}")
            return []

    def get_post_comments(self, post_id):
        """Get comments for a specific post."""
        try:
            response = self.linkedin_client._make_request(
                "GET",
                f"/v2/socialActions/{post_id}/comments",
                params={"count": 100}
            )
            return response.get('elements', [])
        except Exception as e:
            logger.error(f"Error fetching comments for post {post_id}: {str(e)}")
            return []

    def respond_to_comments(self):
        """Check for new comments and respond to them."""
        try:
            # Get recent posts
            recent_posts = self.get_recent_posts()
            logger.info(f"Found {len(recent_posts)} recent posts to check")
            
            for post in recent_posts:
                post_id = post['id']
                post_content = post.get('specificContent', {}).get('com.linkedin.ugc.ShareContent', {}).get('text', {}).get('text', '')
                
                # Get comments for this post
                comments = self.get_post_comments(post_id)
                logger.info(f"Found {len(comments)} comments for post {post_id}")
                
                for comment in comments:
                    comment_id = comment['id']
                    
                    # Skip if we've already processed this comment
                    if comment_id in self.processed_comments:
                        continue
                    
                    # Skip if the comment is from us
                    if comment['actor'] == f"urn:li:person:{self.linkedin_client.get_user_id()}":
                        continue
                    
                    comment_text = comment.get('message', {}).get('text', '')
                    commenter_name = comment.get('actor', '').split(':')[-1]
                    
                    # Generate and post response
                    try:
                        response_text = self.generate_comment_response(comment_text, post_content)
                        
                        # Post the response
                        self.linkedin_client._make_request(
                            "POST",
                            f"/v2/socialActions/{post_id}/comments",
                            json={
                                "actor": f"urn:li:person:{self.linkedin_client.get_user_id()}",
                                "message": {
                                    "text": response_text
                                },
                                "parentComment": f"urn:li:comment:{comment_id}"
                            }
                        )
                        
                        logger.info(f"Responded to comment {comment_id} on post {post_id}")
                        print(f"\nResponded to a comment by {commenter_name}:")
                        print(f"Original comment: {comment_text}")
                        print(f"Response: {response_text}")
                        
                        # Mark comment as processed
                        self.processed_comments.add(comment_id)
                        
                    except Exception as e:
                        logger.error(f"Error responding to comment {comment_id}: {str(e)}")
                        
        except Exception as e:
            logger.error(f"Error in comment response process: {str(e)}")

def main():
    # Initialize components
    linkedin_client = LinkedInAPI(os.getenv('LINKEDIN_ACCESS_TOKEN'))
    comment_responder = CommentResponder(linkedin_client, os.getenv('GOOGLE_API_KEY'))
    
    print("\nStarting LinkedIn Comment Responder...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            comment_responder.respond_to_comments()
            # Check for new comments every 5 minutes
            time.sleep(300)
            
    except KeyboardInterrupt:
        print("\nStopping Comment Responder...")

if __name__ == "__main__":
    main() 