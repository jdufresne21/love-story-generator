#!/usr/bin/env python3
"""
Love Story Generator - Main Terminal Interface
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.story_generator import StoryGenerator
from src.form_handler import FormHandler
from config.settings import Config

def main():
    """Main function to run the Love Story Generator"""
    print("=" * 50)
    print("   Welcome to the Love Story Generator!")
    print("=" * 50)
    print()
    
    # Initialize components
    try:
        config = Config()
        story_generator = StoryGenerator(
            api_key=config.openai_api_key,
            model_name=config.model_name,
            max_tokens=config.max_tokens,
            temperature=config.temperature
        )
        form_handler = FormHandler()
        
        print("Let's create your personalized love story!")
        print("Please answer the following questions:\n")
        
        # Collect form data
        form_data = form_handler.collect_responses()
        
        if not form_data:
            print("No responses collected. Exiting...")
            return
        
        print("\nGenerating your love story...")
        print("-" * 30)
        
        # Generate story using ChatGPT
        story = story_generator.generate_story(form_data)
        
        if story:
            print("\n" + "=" * 50)
            print("   YOUR PERSONALIZED LOVE STORY")
            print("=" * 50)
            print()
            print(story)
            print()
            print("=" * 50)
        else:
            print("Sorry, there was an error generating your story. Please try again.")
            
    except Exception as e:
        print(f"Error: {e}")
        print("Please check your configuration and try again.")

if __name__ == "__main__":
    main()
