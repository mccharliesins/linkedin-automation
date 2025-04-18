import os
import google.generativeai as genai
from datetime import datetime
import random

# Configure the Gemini API
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

# Topics that resonate with tech leaders, managers, and HR
TOPICS = [
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
    "Insightful analysis on {topic}",
    "Practical tips for {topic}",
    "Future trends in {topic}",
    "Case study: Successful {topic} implementation",
    "Expert roundup on {topic}",
    "Data-driven insights on {topic}",
    "Best practices for {topic}",
    "Innovative approaches to {topic}"
]

# Hashtags relevant to the target audience
HASHTAGS = [
    "#TechLeadership", "#HRTech", "#DigitalTransformation", "#FutureOfWork",
    "#LeadershipDevelopment", "#TalentManagement", "#Innovation", "#TechIndustry",
    "#WorkplaceCulture", "#EmployeeEngagement", "#DiversityInTech", "#TechRecruitment",
    "#ManagementTips", "#HRInnovation", "#TechTrends"
]

def generate_content():
    # Select a random topic and content type
    topic = random.choice(TOPICS)
    content_type = random.choice(CONTENT_TYPES).format(topic=topic)
    
    # Generate the prompt
    prompt = f"""Create a LinkedIn post for tech leaders, managers, and HR professionals about {content_type}.
    The post should be:
    - Professional and insightful
    - Data-driven where possible
    - Include practical takeaways
    - Be engaging and thought-provoking
    - Focus on actionable insights
    - Be between 200-300 words
    - Include relevant statistics or research findings
    - End with a thought-provoking question
    
    Format the post with:
    - A compelling opening
    - 2-3 key points
    - A clear conclusion
    - A call to action or question
    """
    
    # Generate the content
    response = model.generate_content(prompt)
    
    # Select 3-5 relevant hashtags
    selected_hashtags = random.sample(HASHTAGS, random.randint(3, 5))
    
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