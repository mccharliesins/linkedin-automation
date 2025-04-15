# LinkedIn Automation AI Agent

This project implements an AI-powered LinkedIn automation system using Python and the official LinkedIn API. The system helps automate various LinkedIn activities while maintaining professional standards and adhering to LinkedIn's terms of service.

## Features

- Automated content creation and posting
- Smart connection management
- Engagement automation (likes, comments)
- Analytics tracking
- Voice control capabilities
- Multi-modal content generation

## Prerequisites

- Python 3.8 or higher
- LinkedIn Developer Account
- Google Gemini API Key
- LinkedIn API Access

## Installation

1. Clone this repository:

```bash
git clone [your-repository-url]
cd linkedin-automation
```

2. Install required dependencies:

```bash
pip install -r requirements.txt
```

3. Set up your environment variables:
   - Copy `.env.example` to `.env`
   - Fill in your API keys and credentials

## Configuration

1. LinkedIn API Setup:

   - Create a LinkedIn Developer Account at https://www.linkedin.com/developers/
   - Create a new application
   - Note down your Client ID and Client Secret
   - Add your application's redirect URL (e.g., http://localhost:8000)
   - Enable the following OAuth 2.0 scopes:
     - `openid`
     - `profile`
     - `email`
     - `w_member_social`

2. Google Gemini API Setup:
   - Visit Google AI Studio (https://makersuite.google.com/app/apikey)
   - Create an API key
   - Add it to your .env file

## Authentication Process

1. First, run the authentication script:

```bash
python linkedin_auth.py
```

2. This will:

   - Open your browser to LinkedIn's authorization page
   - Request necessary permissions
   - Save the access token to your .env file
   - Log the process in `linkedin_auth.log`

3. Verify the token:

```bash
python linkedin_menu.py
```

- Select option 1 to validate your token
- If successful, you'll see your profile information

## Using the Menu Interface

1. Start the menu interface:

```bash
python linkedin_menu.py
```

2. Menu Options:

   - **Create and Post Content**: Generate and post content to LinkedIn
     - Enter a topic
     - Review generated title and content
     - Option to include a URL
     - Confirm before posting
   - **Validate Token**: Check if your access token is valid
   - **Exit**: Close the program

3. Content Creation Process:
   - Enter a topic for your post
   - The system will generate a title and content
   - Review and edit if needed
   - Choose to include a URL (optional)
   - Confirm to post or cancel

## Project Structure

```
linkedin-automation/
├── .env                    # Environment variables
├── requirements.txt        # Python dependencies
├── linkedin_auth.py        # Authentication script
├── linkedin_menu.py        # Menu interface
├── linkedin_api.py         # API wrapper
├── linkedin_agent.py       # Main automation script
├── modules/               # Core functionality modules
│   ├── content.py         # Content generation
│   ├── network.py         # Connection management
│   ├── engagement.py      # Engagement automation
│   └── analytics.py       # Performance tracking
└── README.md              # This file
```

## Security

- All sensitive credentials are stored in the `.env` file
- Never commit your `.env` file to version control
- Use environment variables for all API keys and secrets
- Log files are automatically created and can be reviewed for debugging

## Best Practices

1. Rate Limiting:

   - Implement delays between actions
   - Stay within LinkedIn's API limits
   - Monitor your automation activity

2. Content Quality:

   - Review AI-generated content before posting
   - Maintain professional tone
   - Ensure accuracy of information

3. Network Building:
   - Personalize connection requests
   - Focus on relevant connections
   - Avoid spam-like behavior

## Support

For issues and feature requests, please open an issue in the repository.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
