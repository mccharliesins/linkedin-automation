import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ContentModule:
    def __init__(self, gemini_model, config: Dict[str, Any]):
        self.gemini_model = gemini_model
        self.config = config
        logger.info("Content Module initialized")

    def generate_post(self, topic: str) -> Dict[str, str]:
        """Generate a LinkedIn post about the given topic"""
        try:
            prompt = f"""
            Create a professional LinkedIn post about {topic} with the following specifications:
            - Tone: {self.config['content_tone']}
            - Length: {self.config['content_length']}
            - Include a compelling headline
            - Include 2-3 key points
            - End with a call to action
            - Format for LinkedIn's platform

            Return the response in JSON format with the following structure:
            {{
                "title": "Post Title",
                "text": "Main post content",
                "description": "Brief description",
                "url": "Optional URL",
                "image_url": "Optional image URL"
            }}
            """

            response = self.gemini_model.generate_content(prompt)
            content = self._parse_response(response.text)
            
            logger.info(f"Generated content for topic: {topic}")
            return content
        except Exception as e:
            logger.error(f"Failed to generate content: {str(e)}")
            raise

    def _parse_response(self, response_text: str) -> Dict[str, str]:
        """Parse the Gemini model response into structured content"""
        try:
            # In a real implementation, you would properly parse the JSON response
            # This is a simplified version
            import json
            return json.loads(response_text)
        except json.JSONDecodeError:
            logger.error("Failed to parse content response")
            # Return a default structure if parsing fails
            return {
                "title": "Professional Update",
                "text": response_text,
                "description": "A professional update",
                "url": "",
                "image_url": ""
            }

    def generate_article(self, topic: str) -> Dict[str, str]:
        """Generate a LinkedIn article about the given topic"""
        try:
            prompt = f"""
            Create a professional LinkedIn article about {topic} with the following specifications:
            - Tone: {self.config['content_tone']}
            - Length: 1000-1500 words
            - Include a compelling headline
            - Include 3-5 main sections
            - Include relevant examples and data
            - End with a strong conclusion and call to action

            Return the response in JSON format with the following structure:
            {{
                "title": "Article Title",
                "content": "Main article content",
                "summary": "Brief summary",
                "tags": ["tag1", "tag2", "tag3"]
            }}
            """

            response = self.gemini_model.generate_content(prompt)
            article = self._parse_article_response(response.text)
            
            logger.info(f"Generated article for topic: {topic}")
            return article
        except Exception as e:
            logger.error(f"Failed to generate article: {str(e)}")
            raise

    def _parse_article_response(self, response_text: str) -> Dict[str, str]:
        """Parse the Gemini model response into structured article content"""
        try:
            import json
            return json.loads(response_text)
        except json.JSONDecodeError:
            logger.error("Failed to parse article response")
            return {
                "title": "Professional Article",
                "content": response_text,
                "summary": "A professional article",
                "tags": ["professional", "article"]
            } 