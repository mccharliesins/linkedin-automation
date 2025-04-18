import os
import json
import time
import random
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv
from linkedin_menu import LinkedInAPI

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.getenv('LOG_FILE', 'tech_leadership_content.log')
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Hook styles
HOOK_STYLES = [
    "Your team is struggling, and your {topic} approach might be the reason why.",
    "You're working hard on {topic}, but it's not working like you hoped.",
    "Your team keeps hitting the same wall with {topic}, and it's getting frustrating.",
    "You're not alone - most leaders are getting {topic} wrong without realizing it.",
    "That nagging feeling about {topic}? It's trying to tell you something important.",
    "Your team deserves better than the current {topic} situation.",
    "The way you're handling {topic} might be holding your team back.",
    "You're smart, but {topic} is trickier than it looks."
]

# Major tech hubs in US, Canada, and London with their specific characteristics
LOCATIONS = {
    # US Cities
    "Silicon Valley": {
        "topics": ["Startup Culture", "Venture Capital", "Tech Innovation", "Scale-up Strategies", 
                  "AI Development", "Tech Ecosystem", "Startup Funding", "Tech Talent Pool"],
        "hashtags": ["#SiliconValley", "#SVStartups", "#BayAreaTech", "#TechSV", "#StartupSV"]
    },
    "New York": {
        "topics": ["FinTech", "Corporate Innovation", "Tech in Finance", "Urban Tech Solutions",
                  "Media Tech", "E-commerce", "Tech in Wall Street", "Startup Scene"],
        "hashtags": ["#NYCTech", "#FinTechNYC", "#NYCStartups", "#TechNY", "#NYCInnovation"]
    },
    "Boston": {
        "topics": ["Biotech", "Healthcare Tech", "Education Tech", "Research & Development",
                  "Life Sciences", "Academic Innovation", "Tech in Healthcare"],
        "hashtags": ["#BostonTech", "#BioTech", "#EdTech", "#BostonStartups", "#TechBoston"]
    },
    "Austin": {
        "topics": ["Tech Migration", "Startup Growth", "Tech Events", "Innovation Culture",
                  "Tech Talent Attraction", "Business Relocation", "Tech Community"],
        "hashtags": ["#AustinTech", "#ATXTech", "#TexasTech", "#AustinStartups", "#TechAustin"]
    },
    "Seattle": {
        "topics": ["Cloud Computing", "E-commerce", "Tech Giants", "Software Development",
                  "AI Research", "Tech Infrastructure", "Cloud Services"],
        "hashtags": ["#SeattleTech", "#CloudTech", "#TechSeattle", "#PNWTech", "#SeattleStartups"]
    },
    
    # Canadian Cities
    "Toronto": {
        "topics": ["Canadian Tech Hub", "FinTech Innovation", "AI Development", "Tech Talent",
                  "Startup Ecosystem", "Tech Investment", "Diversity in Tech"],
        "hashtags": ["#TorontoTech", "#CanadianTech", "#TechTO", "#TorontoStartups", "#TechCanada"]
    },
    "Vancouver": {
        "topics": ["Tech in Gaming", "Sustainable Tech", "Clean Tech", "Tech Innovation",
                  "Startup Scene", "Tech Talent", "Pacific Tech Hub"],
        "hashtags": ["#VancouverTech", "#VanTech", "#TechVan", "#VancouverStartups", "#PacificTech"]
    },
    "Montreal": {
        "topics": ["AI Research", "Gaming Industry", "Tech Innovation", "Bilingual Tech Talent",
                  "Startup Culture", "Tech Education", "Creative Tech"],
        "hashtags": ["#MontrealTech", "#MTLTech", "#TechMTL", "#MontrealStartups", "#QuebecTech"]
    },
    
    # London
    "London": {
        "topics": ["FinTech Innovation", "European Tech Market", "Tech Regulation", "International Expansion",
                  "Tech Investment", "Startup Scene", "Tech Talent", "Digital Transformation",
                  "Tech in Finance", "Innovation Culture", "Tech Policy", "Global Tech Hub"],
        "hashtags": ["#LondonTech", "#UKTech", "#TechUK", "#LondonStartups", "#TechLondon",
                    "#FinTechLondon", "#TechInnovation", "#DigitalLondon"]
    }
}

# General topics that resonate with tech leaders, managers, and HR
GENERAL_TOPICS = [
    "Leadership in Tech",
    "Team Management",
    "HR Innovation",
    "Tech Industry Trends",
    "Workplace Culture",
    "Talent Development",
    "Digital Transformation",
    "Remote Work Strategies",
    "Diversity & Inclusion",
    "Employee Engagement",
    "Tech Leadership Skills",
    "Organizational Change",
    "Future of Work",
    "Tech Recruitment",
    "Performance Management"
]

# Content types with specific angles for tech leadership
CONTENT_TYPES = [
    "Insightful analysis on {topic} in {location}",
    "Practical tips for {topic} in the {location} tech scene",
    "Future trends in {topic} specific to {location}",
    "Case study: Successful {topic} implementation in {location}",
    "Expert roundup on {topic} from {location} tech leaders",
    "Data-driven insights on {topic} in the {location} market",
    "Best practices for {topic} in {location}'s tech ecosystem",
    "Innovative approaches to {topic} from {location}"
]

# General hashtags relevant to the target audience
GENERAL_HASHTAGS = [
    "#TechLeadership", "#HRTech", "#DigitalTransformation", "#FutureOfWork",
    "#LeadershipDevelopment", "#TalentManagement", "#Innovation", "#TechIndustry",
    "#WorkplaceCulture", "#EmployeeEngagement", "#DiversityInTech", "#TechRecruitment",
    "#ManagementTips", "#HRInnovation", "#TechTrends"
]

# Emoji sets for different content sections
EMOJIS = {
    "opening": ["🚀", "💡", "🎯", "🌟", "📈", "💼", "🎓", "🔍"],
    "key_points": ["👉", "💡", "🔑", "📌", "✨", "🎯", "💪", "📊"],
    "conclusion": ["💭", "🤔", "💫", "🎉", "🚀", "💡", "🌟", "📝"],
    "call_to_action": ["💬", "🤝", "👥", "💡", "🎯", "🚀", "💫", "🌟"]
}

class TechLeadershipContentGenerator:
    """Generates tech leadership content using Gemini API and posts to LinkedIn."""
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_API_KEY')
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        self.linkedin_client = LinkedInAPI(os.getenv('LINKEDIN_ACCESS_TOKEN'))

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

    def generate_and_post(self):
        """Generate content and post to LinkedIn."""
        try:
            # Generate content
            content = self.generate_content()
            logger.info("Content generated successfully")
            print("\nGenerated content:")
            print("=" * 50)
            print(content)
            print("=" * 50)

            # Post to LinkedIn
            response = self.linkedin_client.submit_share(text=content)
            logger.info(f"Post created successfully! Post ID: {response['updateKey']}")
            print(f"\nPost created successfully! Post ID: {response['updateKey']}")

            # Save to file with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tech_leadership_content_{timestamp}.txt"
            
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
                
            print(f"\nContent saved to {filename}")

        except Exception as e:
            logger.error(f"Error in generate_and_post: {str(e)}")
            print(f"\nError: {str(e)}")

    def generate_content(self):
        """Generate tech leadership content."""
        # Select a random location and its specific topics
        location = random.choice(list(LOCATIONS.keys()))
        location_data = LOCATIONS[location]
        
        # Combine location-specific and general topics
        all_topics = location_data["topics"] + GENERAL_TOPICS
        topic = random.choice(all_topics)
        
        # Select content type and format with location
        content_type = random.choice(CONTENT_TYPES).format(topic=topic, location=location)
        
        # Select a random hook style
        hook_style = random.choice(HOOK_STYLES).format(topic=topic)
        
        # Generate the prompt
        prompt = f"""Create a LinkedIn post for tech leaders, managers, and HR professionals about {content_type}.

        Write this like you're talking to a friend who's a leader. Keep it real and easy to understand.

        Follow this structure:

        1. OPENING (Hook):
        - Use this hook style: {hook_style}
        - Make it feel like you're talking directly to them
        - Keep it simple and honest
        - 1 line maximum

        2. THE REAL PROBLEM:
        - Explain what's actually going wrong
        - Share a simple stat or fact about {location}
        - Make it feel relatable
        - 2-3 lines maximum
        - Use everyday words, no jargon

        3. THE WAY FORWARD:
        - Share simple, practical steps
        - Give real examples from {location}
        - Make it feel doable
        - 3-4 lines maximum
        - Keep it straightforward

        4. THE GOOD NEWS:
        - End with hope and practical next steps
        - Show it's not as hard as it seems
        - Make them feel they can do this
        - 1-2 lines maximum

        Format Requirements:
        - Total length: 150-200 words
        - Use short paragraphs (1-2 lines max)
        - Add line breaks between sections
        - Use 3-4 relevant emojis strategically
        - Use these bullet markers sparingly: 👉 💡 🔑
        - Make it easy to read
        - Plain text only (no markdown)
        - Write like you're having a conversation
        - Use simple words everyone understands
        - Keep it real and honest

        Return only the formatted post text."""
        
        # Generate the content
        response = self._make_request(prompt)
        content = response['candidates'][0]['content']['parts'][0]['text'].strip()
        
        # Remove any asterisks from the content
        content = content.replace('*', '')
        
        # Remove prefix labels like "Story:", "Curious:", etc.
        content_lines = content.split('\n')
        if content_lines and any(content_lines[0].startswith(label) for label in ['Story:', 'Curious:', 'Bold:', 'Relatable:', 'Contrarian:', 'Metric:', 'Question:', 'Revelation:']):
            content_lines[0] = content_lines[0].split(':', 1)[1].strip()
            content = '\n'.join(content_lines)
        
        # Add emojis if they're not already present
        content_lines = content.split('\n')
        if not any(emoji in content_lines[0] for emoji in EMOJIS["opening"]):
            content_lines[0] = f"{random.choice(EMOJIS['opening'])} {content_lines[0]}"
        
        # Add emojis to key points
        for i, line in enumerate(content_lines[1:], 1):
            if line.strip() and not any(emoji in line for emoji in EMOJIS["key_points"]):
                content_lines[i] = f"{random.choice(EMOJIS['key_points'])} {line}"
        
        # Add emoji to conclusion if not present
        if content_lines and not any(emoji in content_lines[-2] for emoji in EMOJIS["conclusion"]):
            content_lines[-2] = f"{random.choice(EMOJIS['conclusion'])} {content_lines[-2]}"
        
        # Add emoji to call to action if not present
        if content_lines and not any(emoji in content_lines[-1] for emoji in EMOJIS["call_to_action"]):
            content_lines[-1] = f"{random.choice(EMOJIS['call_to_action'])} {content_lines[-1]}"
        
        content = '\n'.join(content_lines)
        
        # Combine location-specific and general hashtags
        all_hashtags = location_data["hashtags"] + GENERAL_HASHTAGS
        selected_hashtags = random.sample(all_hashtags, random.randint(5, 7))
        
        # Format the final post
        post = f"{content}\n\n{' '.join(selected_hashtags)}"
        
        return post

def main():
    try:
        generator = TechLeadershipContentGenerator()
        generator.generate_and_post()
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 