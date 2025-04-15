# LinkedIn Automation System

An AI-powered LinkedIn automation system that helps you create and share engaging content on LinkedIn using Python and the LinkedIn API.

## Features

- 🔐 Secure OAuth 2.0 authentication with LinkedIn
- 🤖 AI-powered content generation using Google's Gemini API
- 📝 Smart topic generation with multiple options
- 🎯 Tech-focused content creation for developers
- 🔄 Token validation and management
- 📊 Comprehensive logging and error handling

## Prerequisites

- Python 3.8 or higher
- LinkedIn Developer Account
- Google Cloud Project with Gemini API enabled
- Required Python packages (see requirements.txt)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/mccharliesins/linkedin-automation.git
cd linkedin-automation
```

2. Install required packages:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

## Configuration

### LinkedIn API Setup

1. Create a LinkedIn Developer Application at [LinkedIn Developer Portal](https://www.linkedin.com/developers/apps)
2. Configure OAuth 2.0 settings:
   - Add `http://localhost:8000/callback` as a redirect URL
   - Enable the following OAuth 2.0 scopes:
     - `openid`
     - `profile`
     - `email`
     - `w_member_social`
3. Copy your Client ID and Client Secret to the `.env` file

### Google Gemini API Setup

1. Create a Google Cloud Project
2. Enable the Gemini API
3. Create an API key
4. Add the API key to your `.env` file

## Usage

### Authentication

1. Run the authentication script:

```bash
python linkedin_auth.py
```

2. Follow the prompts to complete the OAuth flow
3. The script will automatically save your access token

### Content Creation

1. Run the main menu:

```bash
python linkedin_menu.py
```

2. Choose from the following options:
   - Create and post tech content
   - Validate your LinkedIn token
   - Exit the program

### Content Generation Process

1. Select a base tech topic from the predefined list
2. The system will generate 5 unique and engaging topic options
3. Choose one of the generated topics or provide your own
4. Review the generated content
5. Optionally include a URL with your post
6. Confirm to post the content to LinkedIn

## Project Structure

- `linkedin_auth.py`: Handles OAuth authentication with LinkedIn
- `linkedin_menu.py`: Main menu interface and content generation
- `linkedin_api.py`: LinkedIn API wrapper for making requests
- `requirements.txt`: Python package dependencies
- `.env.example`: Template for environment variables
- `.gitignore`: Git ignore file for sensitive data

## Security

- Never commit your `.env` file
- Keep your API keys and tokens secure
- Regularly validate and refresh your LinkedIn token
- Follow LinkedIn's API usage guidelines

## Best Practices

- Review generated content before posting
- Maintain a consistent posting schedule
- Engage with comments and discussions
- Follow LinkedIn's content guidelines
- Keep your tech topics relevant and current

## Contributing

Feel free to submit issues and enhancement requests!
