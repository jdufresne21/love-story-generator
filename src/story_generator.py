"""
Story Generator Module - Handles ChatGPT API integration
"""

import openai
from typing import Dict, Optional

class StoryGenerator:
    """Handles love story generation using OpenAI's ChatGPT API"""
    
    def __init__(self, api_key: str, model_name: str = "gpt-4-turbo-preview", max_tokens: int = 2000, temperature: float = 0.7):
        """Initialize the story generator with API key and model settings"""
        if not api_key:
            raise ValueError("OpenAI API key is required")
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        
    def create_prompt(self, form_data: Dict) -> str:
        """Create a detailed prompt based on form responses"""
        
        prompt = f"""You are a creative romance writer. Create a beautiful, heartwarming love story based on the following personal details:

Character Details:
- {form_data.get('name1', 'Alex')} and {form_data.get('name2', 'Jordan')} are the main characters

Their Love Story:
- How they met: {form_data.get('how_met', 'by chance')}
- Favorite memory together: {form_data.get('favorite_memory', 'a special moment')}
- What they love most about each other: {form_data.get('special_thing', 'their deep connection')}
- Special song/phrase/joke: {form_data.get('special_song', 'their unique bond')}

Story Requirements:
- Start with a creative, romantic title for the story (e.g., "A Symphony of Love", "When Stars Align", "The Language of Hearts")
- Write a complete love story (800-1200 words)
- Incorporate their actual meeting story and favorite memory
- Include the specific things they love about each other
- Mention their special song, phrase, or inside joke if provided
- Include romantic dialogue between the characters
- Show their relationship development from meeting to present
- End with a satisfying, romantic conclusion
- Make it heartwarming and uplifting
- Use vivid descriptions and emotional language
- Make it feel personal and unique to their specific relationship

Format the response with the title on the first line, followed by the story content.

Create a story that captures the essence of their real love story and celebrates their unique connection."""

        return prompt
        
    def generate_story(self, form_data: Dict) -> Optional[str]:
        """Generate a love story using ChatGPT"""
        
        # Add debug logging
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            logger.info("Creating prompt...")
            prompt = self.create_prompt(form_data)
            logger.info(f"Prompt created, length: {len(prompt)} characters")
            
            logger.info("Making API call to OpenAI...")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a talented romance novelist who writes beautiful, emotional love stories with vivid descriptions and authentic dialogue."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            logger.info("API call successful, processing response...")
            story = response.choices[0].message.content
            logger.info(f"Story received, length: {len(story) if story else 0} characters")
            
            if story:
                return story.strip()
            return None
            
        except Exception as e:
            logger.error(f"Error generating story: {e}", exc_info=True)
            print(f"Error generating story: {e}")
            return None
            
    def save_story(self, story: Optional[str], filename: Optional[str] = None) -> bool:
        """Save the generated story to a file"""
        
        try:
            if not story:
                print("No story content to save")
                return False
                
            if not filename:
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"data/love_story_{timestamp}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(story)
            
            print(f"Story saved to: {filename}")
            return True
            
        except Exception as e:
            print(f"Error saving story: {e}")
            return False
