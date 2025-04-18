import os
import json
import time
import random
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=os.getenv('LOG_FILE', 'tech_leadership_content.log')
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

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

class TechLeadershipContentGenerator:
    """Generates tech leadership content using Gemini API."""
    def __init__(self, api_key):
        self.api_key = api_key
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

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
        
        # Generate the prompt
        prompt = f"""Create a LinkedIn post for tech leaders, managers, and HR professionals about {content_type}.
        The post should be:
        - Professional and insightful
        - Data-driven where possible
        - Include practical takeaways specific to {location}
        - Be engaging and thought-provoking
        - Focus on actionable insights
        - Be between 200-300 words
        - Include relevant statistics or research findings about {location}
        - End with a thought-provoking question
        
        Format the post with:
        - A compelling opening
        - 2-3 key points specific to {location}
        - A clear conclusion
        - A call to action or question
        
        Important: Do not use any asterisks (*) or bold formatting in the text.
        """
        
        # Generate the content
        response = self._make_request(prompt)
        content = response['candidates'][0]['content']['parts'][0]['text'].strip()
        
        # Remove any asterisks from the content
        content = content.replace('*', '')
        
        # Combine location-specific and general hashtags
        all_hashtags = location_data["hashtags"] + GENERAL_HASHTAGS
        selected_hashtags = random.sample(all_hashtags, random.randint(5, 7))
        
        # Format the final post
        post = f"{content}\n\n{' '.join(selected_hashtags)}"
        
        return post

def main():
    try:
        generator = TechLeadershipContentGenerator(os.getenv('GOOGLE_API_KEY'))
        content = generator.generate_content()
        
        print("Generated Content:")
        print("=" * 50)
        print(content)
        print("=" * 50)
        
        # Save to file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"tech_leadership_content_{timestamp}.txt"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
            
        print(f"\nContent saved to {filename}")
        
    except Exception as e:
        print(f"Error generating content: {str(e)}")

if __name__ == "__main__":
    main() 