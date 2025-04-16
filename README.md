# LinkedIn Automation

An automated system for generating and posting LinkedIn content using GitHub Actions.

## Features

- Automated content generation using AI
- Scheduled posting to LinkedIn
- Different posting schedules for each day of the week
- Comment monitoring and management
- Randomized posting times for natural appearance

## Prerequisites

1. LinkedIn Developer Account

   - Create an account at [LinkedIn Developers Portal](https://developer.linkedin.com/)
   - Create a new application
   - Get your LinkedIn Access Token with the following permissions:
     - `w_member_social`
     - `r_liteprofile`
     - `r_organization_social`

2. Google API Key (for content generation)
   - Set up a Google Cloud Project
   - Enable the Gemini API
   - Create an API key

## Setup Instructions

1. Fork this repository
2. Add your secrets in GitHub repository settings:

   - Go to Settings > Secrets and Variables > Actions
   - Add the following secrets:
     - `LINKEDIN_ACCESS_TOKEN`: Your LinkedIn API access token
     - `GOOGLE_API_KEY`: Your Google API key for Gemini

3. Install dependencies:

```bash
pip install -r requirements.txt
```

## Posting Schedule

The automation runs 10 times per day, with different times for each day of the week:

### Monday

- Posts at :15 past these hours (UTC):
- 02:15, 05:15, 07:15, 09:15, 11:15, 13:15, 15:15, 17:15, 19:15, 21:15

### Tuesday

- Posts at :30 past these hours (UTC):
- 03:30, 06:30, 08:30, 10:30, 12:30, 14:30, 16:30, 18:30, 20:30, 22:30

### Wednesday

- Posts at :45 past these hours (UTC):
- 01:45, 04:45, 07:45, 09:45, 11:45, 13:45, 16:45, 18:45, 20:45, 23:45

### Thursday

- Posts at :20 past these hours (UTC):
- 02:20, 05:20, 08:20, 10:20, 12:20, 14:20, 17:20, 19:20, 21:20, 23:20

### Friday

- Posts at :10 past these hours (UTC):
- 03:10, 06:10, 08:10, 10:10, 12:10, 15:10, 17:10, 19:10, 21:10, 22:10

### Saturday

- Posts at :25 past these hours (UTC):
- 01:25, 04:25, 07:25, 09:25, 11:25, 14:25, 16:25, 18:25, 20:25, 22:25

### Sunday

- Posts at :40 past these hours (UTC):
- 02:40, 05:40, 08:40, 10:40, 12:40, 13:40, 15:40, 17:40, 19:40, 21:40

## Files Description

- `AutomaticPoster.py`: Main script for generating and posting content
- `comment_checker.py`: Script for monitoring and managing post comments
- `linkedin_menu.py`: Menu interface for manual interactions
- `.github/workflows/automatic_poster.yml`: GitHub Actions workflow configuration

## Configuration

You can modify the posting schedule by editing the cron expressions in `.github/workflows/automatic_poster.yml`.

## Troubleshooting

Common issues and solutions:

1. API Authentication Errors

   - Verify your LinkedIn access token is valid and not expired
   - Check if you have the correct API permissions
   - Ensure your secrets are properly set in GitHub

2. Rate Limiting

   - LinkedIn has API rate limits
   - The schedule is designed to stay within these limits
   - If you hit rate limits, consider reducing the posting frequency

3. Content Generation Issues
   - Verify your Google API key is valid
   - Check if you have billing enabled for the Gemini API
   - Ensure you have sufficient API quota

## Security Notes

- Never commit your API keys or tokens
- Use GitHub secrets for sensitive information
- Regularly rotate your access tokens
- Monitor your application's activity

## Contributing

Feel free to submit issues and enhancement requests!

## License

[MIT License](LICENSE)
