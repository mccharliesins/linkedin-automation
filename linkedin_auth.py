import os
import json
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlencode, parse_qs
import requests
from dotenv import load_dotenv
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='linkedin_auth.log'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# LinkedIn OAuth Configuration
CLIENT_ID = os.getenv('LINKEDIN_CLIENT_ID')
CLIENT_SECRET = os.getenv('LINKEDIN_CLIENT_SECRET')
REDIRECT_URI = os.getenv('LINKEDIN_REDIRECT_URI')
SCOPES = [
    'openid',  # Required for OpenID Connect
    'profile', # For member's lite profile (id, name, picture)
    'email',   # For member's email address
    'w_member_social'  # For posting content
]

def validate_config():
    """Validate required configuration values"""
    missing_vars = []
    if not CLIENT_ID:
        missing_vars.append('LINKEDIN_CLIENT_ID')
    if not CLIENT_SECRET:
        missing_vars.append('LINKEDIN_CLIENT_SECRET')
    if not REDIRECT_URI:
        missing_vars.append('LINKEDIN_REDIRECT_URI')
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle the OAuth callback"""
        try:
            # Extract code from callback URL
            if '?code=' in self.path:
                code = parse_qs(self.path.split('?')[1])['code'][0]
                logger.info("Received authorization code")
                
                access_token = self.exchange_code_for_token(code)
                
                if access_token:
                    self.update_env_file(access_token)
                    self.send_success_response()
                else:
                    self.send_error_response("Failed to get access token")
            else:
                error = parse_qs(self.path.split('?')[1]).get('error', ['Unknown error'])[0]
                error_description = parse_qs(self.path.split('?')[1]).get('error_description', [''])[0]
                self.send_error_response(f"{error}: {error_description}")
                
        except Exception as e:
            logger.error(f"Error in callback handler: {str(e)}")
            self.send_error_response(str(e))

    def exchange_code_for_token(self, code):
        """Exchange authorization code for access token"""
        try:
            token_url = 'https://www.linkedin.com/oauth/v2/accessToken'
            data = {
                'grant_type': 'authorization_code',
                'code': code,
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET,
                'redirect_uri': REDIRECT_URI
            }
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            }
            
            logger.info("Exchanging code for access token...")
            response = requests.post(token_url, data=data, headers=headers)
            
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data.get('access_token')
                id_token = token_data.get('id_token')  # OpenID Connect ID Token
                
                if access_token:
                    logger.info("Successfully obtained access token")
                    if id_token:
                        logger.info("Successfully obtained ID token")
                    return access_token
                else:
                    logger.error("No access token in response")
                    return None
            elif response.status_code == 429:
                retry_after = response.headers.get('Retry-After', 60)
                logger.warning(f"Rate limit exceeded. Waiting {retry_after} seconds before retry")
                time.sleep(int(retry_after))
                return self.exchange_code_for_token(code)
            else:
                logger.error(f"Token exchange failed: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            return None

    def update_env_file(self, access_token):
        """Update .env file with the new access token"""
        try:
            env_path = '.env'
            env_lines = []
            
            # Read existing .env file if it exists
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    env_lines = f.readlines()
            
            # Update or add LINKEDIN_ACCESS_TOKEN
            token_line = f'LINKEDIN_ACCESS_TOKEN={access_token}\n'
            token_updated = False
            
            for i, line in enumerate(env_lines):
                if line.startswith('LINKEDIN_ACCESS_TOKEN='):
                    env_lines[i] = token_line
                    token_updated = True
                    break
            
            if not token_updated:
                env_lines.append(token_line)
            
            # Write back to .env file
            with open(env_path, 'w') as f:
                f.writelines(env_lines)
                
            logger.info("Successfully updated .env file with access token")
            
        except Exception as e:
            logger.error(f"Error updating .env file: {str(e)}")
            raise

    def send_success_response(self):
        """Send success HTML response"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        success_html = """
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 40px auto; text-align: center;">
                <h1 style="color: #0077B5;">Authorization Successful! 🎉</h1>
                <p>Your LinkedIn access token has been saved. You can close this window and return to the application.</p>
                <p style="margin-top: 20px; padding: 10px; background-color: #f0f0f0; border-radius: 5px;">
                    The access token has been automatically saved to your .env file.
                </p>
            </body>
        </html>
        """
        self.wfile.write(success_html.encode())

    def send_error_response(self, error_message):
        """Send error HTML response"""
        self.send_response(400)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        error_html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 40px auto; text-align: center;">
                <h1 style="color: #ff4444;">Authorization Failed ❌</h1>
                <p>An error occurred during the authorization process:</p>
                <p style="margin-top: 20px; padding: 10px; background-color: #fff0f0; border-radius: 5px; color: #ff4444;">
                    {error_message}
                </p>
                <p>Please close this window and try again.</p>
            </body>
        </html>
        """
        self.wfile.write(error_html.encode())

def start_oauth_flow():
    """Start the OAuth flow by opening the authorization URL"""
    try:
        # Validate configuration
        validate_config()
        
        # Construct authorization URL
        auth_params = {
            'response_type': 'code',
            'client_id': CLIENT_ID,
            'redirect_uri': REDIRECT_URI,
            'scope': ' '.join(SCOPES),
            'state': 'random_state_string'  # In production, use a secure random string
        }
        
        auth_url = f"https://www.linkedin.com/oauth/v2/authorization?{urlencode(auth_params)}"
        
        # Start local server to handle callback
        server_address = ('localhost', 8000)
        httpd = HTTPServer(server_address, OAuthHandler)
        
        logger.info("Starting OAuth flow...")
        logger.info("Opening browser for authorization...")
        webbrowser.open(auth_url)
        
        logger.info("Waiting for callback on http://localhost:8000...")
        httpd.handle_request()  # Handle single request
        
    except Exception as e:
        logger.error(f"Error in OAuth flow: {str(e)}")
        raise

if __name__ == "__main__":
    print("Starting LinkedIn Authorization Process...")
    print("This will open your browser to authorize the application.")
    print("Make sure you're logged into LinkedIn before proceeding.")
    input("Press Enter to continue...")
    
    start_oauth_flow() 