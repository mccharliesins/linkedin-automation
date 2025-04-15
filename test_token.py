import os
from dotenv import load_dotenv
import requests
import logging
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='token_test.log'
)
logger = logging.getLogger(__name__)

def test_token():
    # Load environment variables
    load_dotenv()
    access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
    
    if not access_token:
        logger.error("No access token found in .env file")
        return False
        
    # Test endpoints
    base_url = "https://api.linkedin.com/v2"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0',
        'LinkedIn-Version': '202304'
    }
    
    # Test 1: Get user profile using /userinfo endpoint
    try:
        userinfo_response = requests.get(f"{base_url}/userinfo", headers=headers)
        logger.info(f"Profile response status: {userinfo_response.status_code}")
        logger.info(f"Profile response: {userinfo_response.text}")
        
        if userinfo_response.status_code == 200:
            profile_data = userinfo_response.json()
            user_id = profile_data.get('sub')
            logger.info(f"Successfully retrieved profile. User ID: {user_id}")
            
            # Test 2: Create a test post
            post_data = {
                "author": f"urn:li:member:{user_id}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": "This is a test post. It will be deleted immediately."
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            logger.info(f"Attempting to create post with body: {json.dumps(post_data, indent=2)}")
            
            post_response = requests.post(
                f"{base_url}/ugcPosts",
                headers=headers,
                json=post_data
            )
            
            logger.info(f"Post response status: {post_response.status_code}")
            logger.info(f"Post response: {post_response.text}")
            
            if post_response.status_code in [200, 201]:
                logger.info("Successfully created test post")
                return True
            else:
                logger.error(f"Failed to create test post: {post_response.text}")
                return False
        else:
            logger.error(f"Failed to get profile: {userinfo_response.status_code} - {userinfo_response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Error testing token: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing LinkedIn access token...")
    success = test_token()
    print(f"Token test {'successful' if success else 'failed'}. Check token_test.log for details.") 