"""
Form Handler Module - Collects user input for love story generation
"""

from typing import Dict

class FormHandler:
    """Handles form data collection from terminal input"""
    
    def __init__(self):
        """Initialize the form handler"""
        self.questions = [
            {
                'key': 'name1',
                'question': 'What is the first character\'s name?',
                'default': 'Alex'
            },
            {
                'key': 'name2', 
                'question': 'What is the second character\'s name?',
                'default': 'Jordan'
            },
            {
                'key': 'setting',
                'question': 'Where does your love story take place? (e.g., Paris, a small coffee shop, university campus)',
                'default': 'a charming small town'
            },
            {
                'key': 'how_met',
                'question': 'How did they first meet?',
                'default': 'by chance at a bookstore'
            },
            {
                'key': 'shared_interest',
                'question': 'What do they both love or have in common?',
                'default': 'reading and writing'
            },
            {
                'key': 'challenge',
                'question': 'What challenge or obstacle did they have to overcome?',
                'default': 'long distance relationship'
            },
            {
                'key': 'special_thing',
                'question': 'What makes their love story special or unique?',
                'default': 'their ability to understand each other without words'
            },
            {
                'key': 'story_length',
                'question': 'How long should the story be? (short/medium/long)',
                'default': 'medium'
            }
        ]
    
    def collect_responses(self) -> Dict:
        """Collect responses from user input"""
        
        responses = {}
        
        print("Please answer the following questions to create your personalized love story:")
        print("(Press Enter to use the default value shown in brackets)\n")
        
        for question_data in self.questions:
            key = question_data['key']
            question = question_data['question']
            default = question_data['default']
            
            response = input(f"{question} [{default}]: ").strip()
            
            # Use default if no response provided
            if not response:
                response = default
            
            responses[key] = response
        
        return responses
    
    def display_responses(self, responses: Dict):
        """Display collected responses for confirmation"""
        
        print("\n" + "="*40)
        print("Your Love Story Details:")
        print("="*40)
        
        labels = {
            'name1': 'First Character',
            'name2': 'Second Character', 
            'setting': 'Setting',
            'how_met': 'How They Met',
            'shared_interest': 'Shared Interest',
            'challenge': 'Challenge',
            'special_thing': 'What Makes It Special',
            'story_length': 'Story Length'
        }
        
        for key, value in responses.items():
            label = labels.get(key, key.title())
            print(f"{label}: {value}")
        
        print("="*40)
        
        return input("\nLook good? (y/n): ").lower().startswith('y')
    
    def validate_responses(self, responses: Dict) -> bool:
        """Validate that we have minimum required responses"""
        
        required_fields = ['name1', 'name2', 'setting']
        
        for field in required_fields:
            if not responses.get(field):
                print(f"Error: {field} is required")
                return False
        
        return True
