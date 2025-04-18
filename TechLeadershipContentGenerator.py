import os
import google.generativeai as genai
from datetime import datetime
import random

# Configure the Gemini API
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

# Major tech hubs and their specific characteristics
LOCATIONS = {
    "Silicon Valley": {
        "topics": ["Startup Culture", "Venture Capital", "Tech Innovation", "Scale-up Strategies"],
        "hashtags": ["#SiliconValley", "#SVStartups", "#BayAreaTech"]
    },
    "New York": {
        "topics": ["FinTech", "Corporate Innovation", "Tech in Finance", "Urban Tech Solutions"],
        "hashtags": ["#NYCTech", "#FinTechNYC", "#NYCStartups"]
    },
    "London": {
        "topics": ["FinTech Innovation", "European Tech Market", "Tech Regulation", "International Expansion"],
        "hashtags": ["#LondonTech", "#UKTech", "#TechUK"]
    },
    "Berlin": {
        "topics": ["European Startup Scene", "Tech Talent in EU", "Sustainable Tech", "B2B Tech"],
        "hashtags": ["#BerlinTech", "#GermanTech", "#EUTech"]
    },
    "Singapore": {
        "topics": ["Asian Tech Market", "Smart Cities", "APAC Expansion", "Tech in Southeast Asia"],
        "hashtags": ["#SingaporeTech", "#SGStartups", "#APACTech"]
    },
    "Bangalore": {
        "topics": ["Indian Tech Ecosystem", "Global Tech Services", "Tech Talent Pool", "Emerging Markets"],
        "hashtags": ["#BangaloreTech", "#IndianTech", "#TechIndia"]
    },
    "Tel Aviv": {
        "topics": ["Deep Tech", "Cybersecurity", "Tech Innovation", "Startup Nation"],
        "hashtags": ["#TelAvivTech", "#IsraeliTech", "#CyberTech"]
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

def generate_content():
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
    """
    
    # Generate the content
    response = model.generate_content(prompt)
    
    # Combine location-specific and general hashtags
    all_hashtags = location_data["hashtags"] + GENERAL_HASHTAGS
    selected_hashtags = random.sample(all_hashtags, random.randint(5, 7))
    
    # Format the final post
    post = f"{response.text}\n\n{' '.join(selected_hashtags)}"
    
    return post

def main():
    try:
        content = generate_content()
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