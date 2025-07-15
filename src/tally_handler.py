"""
Tally Form Handler - Processes Tally form submissions for love story generation
"""

import json
import os
from typing import Dict, Optional
from datetime import datetime
import hashlib

class TallyHandler:
    """Handles Tally form submissions and converts them to story generation format"""
    
    def __init__(self):
        """Initialize the Tally handler"""
        self.form_fields_mapping = {
            # Map form field names to our internal keys
            'name1': ['your_name', 'name1', 'character1', 'first_character', 'protagonist1'],
            'name2': ['partner_name', 'name2', 'character2', 'second_character', 'protagonist2'],
            'setting': ['setting', 'location', 'place', 'where'],
            'how_met': ['how_met', 'meeting', 'first_meet', 'encounter'],
            'shared_interest': ['shared_interest', 'common_interest', 'hobby', 'passion'],
            'challenge': ['challenge', 'obstacle', 'conflict', 'difficulty'],
            'special_thing': ['love_most', 'special_thing', 'unique', 'special', 'what_makes_special'],
            'story_length': ['story_length', 'length', 'duration']
        }
        
        # Default values for missing fields
        self.defaults = {
            'name1': 'Alex',
            'name2': 'Jordan',
            'setting': 'a charming small town',
            'how_met': 'by chance at a bookstore',
            'shared_interest': 'reading and writing',
            'challenge': 'long distance relationship',
            'special_thing': 'their ability to understand each other without words',
            'story_length': 'medium'
        }
    
    def process_tally_webhook(self, webhook_data: Dict) -> Dict:
        """Process incoming Tally webhook data and convert to story format"""
        
        try:
            # Extract form responses from Tally webhook
            form_responses = webhook_data.get('eventBody', {}).get('event', {}).get('formResponses', [])
            
            if not form_responses:
                raise ValueError("No form responses found in webhook data")
            
            # Get the latest response
            latest_response = form_responses[0]
            answers = latest_response.get('answers', [])
            
            # Convert Tally answers to our format
            story_data = self._convert_tally_answers(answers)
            
            # Add metadata
            story_data['submission_id'] = latest_response.get('responseId', '')
            story_data['submitted_at'] = latest_response.get('submittedAt', '')
            story_data['form_id'] = webhook_data.get('eventBody', {}).get('event', {}).get('formId', '')
            
            return story_data
            
        except Exception as e:
            print(f"Error processing Tally webhook: {e}")
            return {}
    
    def _convert_tally_answers(self, answers: list) -> Dict:
        """Convert Tally answer format to our story data format"""
        
        story_data = {}
        
        for answer in answers:
            field_id = answer.get('fieldId', '')
            field_value = answer.get('value', '')
            
            # Map Tally field to our internal key
            internal_key = self._map_tally_field(field_id, field_value)
            
            if internal_key:
                story_data[internal_key] = field_value
        
        # Fill in missing fields with defaults
        for key, default_value in self.defaults.items():
            if key not in story_data:
                story_data[key] = default_value
        
        return story_data
    
    def _map_tally_field(self, field_id: str, field_value: str) -> Optional[str]:
        """Map Tally field ID to our internal field key"""
        
        # This is a simplified mapping - you'll need to update this based on your actual Tally form
        # You can get the field IDs from your Tally form webhook test
        
        # Common field name patterns
        field_lower = field_id.lower()
        
        for internal_key, possible_names in self.form_fields_mapping.items():
            for name in possible_names:
                if name in field_lower or field_lower in name:
                    return internal_key
        
        # If no match found, try to guess based on field value content
        if 'name' in field_lower:
            return 'name1'  # We'll handle name2 in the conversion logic
        elif 'place' in field_lower or 'where' in field_lower:
            return 'setting'
        elif 'meet' in field_lower or 'encounter' in field_lower:
            return 'how_met'
        elif 'interest' in field_lower or 'hobby' in field_lower:
            return 'shared_interest'
        elif 'challenge' in field_lower or 'obstacle' in field_lower:
            return 'challenge'
        elif 'special' in field_lower or 'unique' in field_lower:
            return 'special_thing'
        elif 'length' in field_lower or 'duration' in field_lower:
            return 'story_length'
        
        return None
    
    def validate_story_data(self, story_data: Dict) -> bool:
        """Validate that we have minimum required data for story generation"""
        
        required_fields = ['name1', 'name2', 'setting']
        
        for field in required_fields:
            if not story_data.get(field):
                print(f"Error: {field} is required")
                return False
        
        return True
    
    def save_submission(self, story_data: Dict, story_text: Optional[str] = None) -> str:
        """Save the form submission and story to a file"""
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            submission_id = story_data.get('submission_id', f'submission_{timestamp}')
            
            # Create filename
            filename = f"data/submission_{timestamp}_{submission_id[:8]}.json"
            
            # Prepare data to save
            save_data = {
                'submission_data': story_data,
                'generated_at': timestamp,
                'story_text': story_text
            }
            
            # Ensure data directory exists
            os.makedirs('data', exist_ok=True)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            print(f"Submission saved to: {filename}")
            return filename
            
        except Exception as e:
            print(f"Error saving submission: {e}")
            return "" 