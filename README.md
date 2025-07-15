# Love Story Generator

A simple Python application that generates personalized love stories using OpenAI's ChatGPT API.

## Features

- Terminal-based interface for collecting story details
- Integration with ChatGPT (gpt-4o-mini model) for story generation
- Customizable story parameters (characters, setting, challenges, etc.)
- Story saving functionality
- Ready for future Tally integration

## Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Configure your API key:
   - Copy `.env.example` to `.env`
   - Add your OpenAI API key to the `.env` file

3. Run the application:
```bash
python main.py
```

## Project Structure

```
love_story_generator/
├── main.py              # Main application entry point
├── requirements.txt     # Python dependencies
├── .env.example        # Environment variables template
├── config/
│   ├── __init__.py
│   └── settings.py     # Configuration management
├── src/
│   ├── __init__.py
│   ├── story_generator.py  # ChatGPT API integration
│   └── form_handler.py     # User input collection
└── data/               # Generated stories storage
```

## Usage

1. Run the application with `python main.py`
2. Answer the prompts about your love story
3. Wait for ChatGPT to generate your personalized story
4. Your story will be displayed and optionally saved to the data folder

## Future Enhancements

- Tally form integration
- Web interface
- Multiple story templates
- Character relationship dynamics
- Story export options
