import os
import requests
from dotenv import load_dotenv
import logging
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='linkedin_api.log'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class LinkedInAPI:
    def __init__(self, access_token):
        """Initialize the LinkedIn API client with an access token."""
        self.access_token = access_token
        self.base_url = "https://api.linkedin.com/v2"
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0',
            'LinkedIn-Version': '202304'
        }

    def get_profile(self):
        """Get the user's profile information using OpenID Connect userinfo endpoint."""
        try:
            response = requests.get(
                f"{self.base_url}/userinfo",  # OpenID Connect userinfo endpoint
                headers=self.headers
            )
            
            if response.status_code == 200:
                profile_data = response.json()
                logger.info(f"Successfully retrieved user profile: {profile_data.get('name')}")
                return profile_data
            else:
                logger.error(f"Failed to get profile: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            return None

    def get_user_id(self):
        """Get the user's LinkedIn ID from the OpenID Connect userinfo response."""
        profile = self.get_profile()
        if profile and 'sub' in profile:  # 'sub' is the user identifier in OpenID Connect
            return profile['sub']
        return None

    def submit_share(self, text, url=None, title=None, description=None):
        """Submit a share to LinkedIn."""
        try:
            # Get the user's ID
            user_id = self.get_user_id()
            if not user_id:
                logger.error("Failed to get user ID")
                return None

            # Construct the request body
            share_body = {
                "author": f"urn:li:member:{user_id}",  # Using member URN format
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

            # If URL is provided, add it to the share
            if url:
                share_body["specificContent"]["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "ARTICLE"
                share_body["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [{
                    "status": "READY",
                    "description": {
                        "text": description or ""
                    },
                    "originalUrl": url,
                    "title": {
                        "text": title or ""
                    }
                }]

            logger.info(f"Sending share request with body: {json.dumps(share_body, indent=2)}")
            
            # Make the API request
            response = requests.post(
                f"{self.base_url}/ugcPosts",
                headers=self.headers,
                json=share_body
            )

            if response.status_code in [200, 201]:
                logger.info("Successfully created share")
                return response.json()
            else:
                logger.error(f"Failed to create share: {response.status_code} - {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            return None

    def validate_token(self):
        """Validate the access token by attempting to get the user's profile."""
        try:
            response = requests.get(
                f"{self.base_url}/userinfo",  # Using OpenID Connect userinfo endpoint
                headers=self.headers
            )
            if response.status_code == 200:
                profile = response.json()
                logger.info(f"Token validated successfully for user: {profile.get('name')}")
                return True
            return False
        except requests.exceptions.RequestException:
            return False 