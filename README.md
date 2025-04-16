# LinkedIn Automation

An automated system for generating and posting LinkedIn content using GitHub Actions.

## Features

- Automated content generation using AI
- Scheduled posting to LinkedIn with completely randomized timing
- Different posting schedules for each day of the week
- Comment monitoring and management
- Natural posting pattern with random intervals

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

The automation runs 10 times per day with completely randomized times for each day of the week. This creates a natural posting pattern that doesn't follow any fixed schedule:

### Monday (UTC)

- 03:17, 06:42, 09:08, 11:53, 14:27, 16:11, 18:38, 20:22, 22:49, 23:05

### Tuesday (UTC)

- 02:31, 05:57, 07:19, 10:44, 13:03, 15:36, 17:51, 19:07, 21:29, 23:46

### Wednesday (UTC)

- 01:23, 04:48, 07:12, 09:37, 12:55, 15:14, 17:41, 20:09, 22:33, 23:58

### Thursday (UTC)

- 02:16, 04:43, 07:07, 10:52, 13:28, 16:13, 18:39, 20:21, 22:47, 23:04

### Friday (UTC)

- 01:26, 03:54, 06:18, 09:45, 12:02, 14:35, 16:50, 19:06, 21:31, 23:59

### Saturday (UTC)

- 02:24, 04:51, 07:15, 10:40, 13:01, 15:34, 17:53, 20:08, 22:32, 23:57

### Sunday (UTC)

- 01:20, 03:46, 06:11, 09:38, 11:56, 14:15, 16:42, 19:03, 21:30, 23:55

Each day has:

- 10 completely random posting times
- No fixed intervals between posts
- Different minutes for each post
- Varied distribution throughout the day
- Natural, unpredictable pattern

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
