"""
Universal Story Generator - Creates personalized content for any occasion
"""

import openai
from typing import Dict, Optional
import json
from datetime import datetime

class UniversalGenerator:
    """Generates personalized content for various occasions and types"""
    
    def __init__(self, api_key: str, model_name: str = "gpt-4-turbo-preview", max_tokens: int = 2000, temperature: float = 0.7):
        """Initialize the universal generator"""
        self.client = openai.OpenAI(api_key=api_key)
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        # Content type templates
        self.templates = {
            'love_story': self._get_love_story_template(),
            'wedding_speech': self._get_wedding_speech_template(),
            'eulogy': self._get_eulogy_template(),
            'birthday_speech': self._get_birthday_speech_template(),
            'anniversary_speech': self._get_anniversary_speech_template(),
            'graduation_speech': self._get_graduation_speech_template(),
            'retirement_speech': self._get_retirement_speech_template(),
            'toast': self._get_toast_template(),
            'tribute': self._get_tribute_template(),
            'custom': self._get_custom_template()
        }
    
    def generate_content(self, form_data: Dict) -> Optional[str]:
        """Generate personalized content based on form data"""
        try:
            # Extract form data
            content_type = form_data.get('content_type', 'custom')
            tone = form_data.get('tone', 'heartfelt')
            speaker_name = form_data.get('speaker_name', '')
            recipient_name = form_data.get('recipient_name', '')
            relationship = form_data.get('relationship', '')
            occasion = form_data.get('occasion', '')
            key_memories = form_data.get('key_memories', '')
            traits = form_data.get('traits', '')
            quotes_phrases = form_data.get('quotes_phrases', '')
            length = form_data.get('length', 'medium')
            custom_type = form_data.get('custom_type', '')
            
            # Get the appropriate template
            template = self.templates.get(content_type, self.templates['custom'])
            
            # Build the prompt
            prompt = self._build_prompt(
                template=template,
                content_type=content_type,
                tone=tone,
                speaker_name=speaker_name,
                recipient_name=recipient_name,
                relationship=relationship,
                occasion=occasion,
                key_memories=key_memories,
                traits=traits,
                quotes_phrases=quotes_phrases,
                length=length,
                custom_type=custom_type
            )
            
            # Generate content using OpenAI
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a professional writer specializing in creating personalized, heartfelt content for special occasions. You excel at capturing the essence of relationships and creating meaningful, engaging content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            content = response.choices[0].message.content
            return content.strip() if content else None
            
        except Exception as e:
            print(f"Error generating content: {e}")
            return None
    
    def _build_prompt(self, **kwargs) -> str:
        """Build the prompt for content generation"""
        template = kwargs.get('template', '')
        content_type = kwargs.get('content_type', 'custom')
        tone = kwargs.get('tone', 'heartfelt')
        length = kwargs.get('length', 'medium')
        
        # Add length guidance
        length_guidance = {
            'short': 'Keep this concise (approximately 150-250 words)',
            'medium': 'Make this moderate in length (approximately 300-500 words)',
            'long': 'Make this comprehensive (approximately 600-800 words)',
            'very_long': 'Make this detailed and extensive (approximately 800-1200 words)'
        }
        
        # Add tone guidance
        tone_guidance = {
            'romantic': 'Use romantic, passionate language with poetic elements',
            'heartfelt': 'Use warm, sincere, and emotionally touching language',
            'humorous': 'Include humor, wit, and light-hearted moments while staying respectful',
            'formal': 'Use formal, professional language appropriate for the occasion',
            'casual': 'Use conversational, friendly language',
            'inspirational': 'Use uplifting, motivational language that inspires',
            'nostalgic': 'Use reflective, memory-focused language that evokes the past',
            'celebratory': 'Use joyful, celebratory language that conveys excitement',
            'reverent': 'Use respectful, dignified language appropriate for solemn occasions'
        }
        
        prompt = f"""
{template}

**Content Type:** {content_type.replace('_', ' ').title()}
**Tone:** {tone_guidance.get(tone, tone)}
**Length:** {length_guidance.get(length, length)}

**Speaker:** {kwargs.get('speaker_name', '')}
**Recipient(s):** {kwargs.get('recipient_name', '')}
**Relationship:** {kwargs.get('relationship', '')}
**Occasion:** {kwargs.get('occasion', '')}

**Key Memories & Stories:**
{kwargs.get('key_memories', '')}

**Special Traits & Qualities:**
{kwargs.get('traits', '')}

**Special Quotes or Phrases:**
{kwargs.get('quotes_phrases', '')}

Please create a personalized, engaging piece that captures the essence of this relationship and occasion. Make it feel authentic and meaningful to the specific people and situation described.
"""
        
        return prompt
    
    def _get_love_story_template(self) -> str:
        return """Create a beautiful, romantic love story that reads like a fairy tale come to life. 
        Begin with a creative, engaging title that captures the essence of their love. 
        Weave together their memories and traits into a narrative that celebrates their unique bond. 
        Use romantic language and create a story that feels magical and timeless."""
    
    def _get_wedding_speech_template(self) -> str:
        return """Create a heartfelt wedding speech that celebrates the couple's love and journey together. 
        Include personal anecdotes, well-wishes for their future, and words of wisdom about marriage. 
        Make it appropriate for a wedding ceremony or reception, balancing humor with sincerity."""
    
    def _get_eulogy_template(self) -> str:
        return """Create a respectful and meaningful eulogy that honors the person's life and legacy. 
        Focus on their positive qualities, meaningful contributions, and the impact they had on others. 
        Include personal memories and stories that capture their essence. 
        Use dignified, reverent language appropriate for a memorial service."""
    
    def _get_birthday_speech_template(self) -> str:
        return """Create a celebratory birthday speech that honors the person and their special day. 
        Include personal stories, achievements, and reasons why they're loved and appreciated. 
        Make it joyful and uplifting, perfect for a birthday celebration."""
    
    def _get_anniversary_speech_template(self) -> str:
        return """Create a romantic anniversary speech that celebrates the couple's journey together. 
        Reflect on their shared memories, growth as a couple, and the love that has sustained them. 
        Include hopes for their future together and appreciation for their partnership."""
    
    def _get_graduation_speech_template(self) -> str:
        return """Create an inspirational graduation speech that celebrates the graduate's achievements and future potential. 
        Include words of encouragement, advice for the future, and recognition of their hard work. 
        Make it motivational and forward-looking while honoring their accomplishments."""
    
    def _get_retirement_speech_template(self) -> str:
        return """Create a respectful retirement speech that honors the person's career and contributions. 
        Reflect on their professional journey, achievements, and the impact they've made. 
        Include well-wishes for their retirement and recognition of their dedication and service."""
    
    def _get_toast_template(self) -> str:
        return """Create a warm and engaging toast that celebrates the person or occasion. 
        Include personal anecdotes, well-wishes, and reasons for celebration. 
        Make it concise but meaningful, perfect for raising a glass in their honor."""
    
    def _get_tribute_template(self) -> str:
        return """Create a heartfelt tribute that honors and celebrates the person's life, achievements, or qualities. 
        Include personal stories, meaningful memories, and recognition of what makes them special. 
        Make it personal and authentic, capturing the essence of who they are."""
    
    def _get_custom_template(self) -> str:
        return """Create a personalized piece of content that fits the specific occasion and relationship described. 
        Adapt the style and tone to match the content type and occasion. 
        Make it meaningful, authentic, and appropriate for the specific situation.""" 