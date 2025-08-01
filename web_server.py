#!/usr/bin/env python3
"""
Web Server for Love Story Generator - Handles Tally form webhooks
"""

from flask import Flask, request, jsonify, render_template_string, render_template, flash, redirect, url_for
from flask_login import LoginManager, login_required, current_user, login_user, logout_user
import json
import os
import sys
import datetime
from io import BytesIO
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import user models and auth
from src.user_models import db, User, Story
from src.auth import auth
from src.payments import PaymentProcessor

# PDF generation imports
PDF_AVAILABLE = False
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.colors import HexColor, Color
    from reportlab.lib.units import inch
    from reportlab.pdfgen import canvas
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    PDF_AVAILABLE = True
except ImportError:
    # PDF generation will fall back to text files
    pass

# Helper function to safely create colors (defined globally)
def safe_color(hex_code):
    if not PDF_AVAILABLE:
        return None
    try:
        return HexColor(hex_code)
    except:
        # Fallback to basic colors if HexColor fails
        color_map = {
            '#c44569': Color(0.77, 0.27, 0.41),  # Pink
            '#667eea': Color(0.40, 0.49, 0.92),  # Blue
            '#333333': Color(0.20, 0.20, 0.20),  # Dark gray
            '#666666': Color(0.40, 0.40, 0.40),  # Gray
            '#28a745': Color(0.16, 0.65, 0.27),  # Green
        }
        return color_map.get(hex_code, Color(0, 0, 0))  # Default to black

from src.story_generator import StoryGenerator
from src.universal_generator import UniversalGenerator
from src.tally_handler import TallyHandler
from config.settings import Config

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///love_stories.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database and login manager
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register blueprints
app.register_blueprint(auth, url_prefix='/auth')

# Initialize components
config = Config()

# Validate API key before creating story generator
if not config.openai_api_key:
    raise ValueError("OpenAI API key is required. Please set the OPENAI_API_KEY environment variable.")

story_generator = StoryGenerator(
    api_key=config.openai_api_key,
    model_name=config.model_name,
    max_tokens=config.max_tokens,
    temperature=config.temperature
)
universal_generator = UniversalGenerator(
    api_key=config.openai_api_key,
    model_name=config.model_name,
    max_tokens=config.max_tokens,
    temperature=config.temperature
)
tally_handler = TallyHandler()

# HTML template for displaying the story
STORY_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your Story - Told with Love</title>
    <style>
        body {
            font-family: 'Georgia', serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .story-container {
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin: 20px 0;
        }
        .story-title {
            text-align: center;
            color: #333;
            font-size: 2.5em;
            margin-bottom: 30px;
            font-weight: 300;
        }
        .story-content {
            font-size: 1.1em;
            color: #444;
            text-align: justify;
            white-space: pre-wrap;
        }
        .story-meta {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-top: 30px;
            border-left: 4px solid #667eea;
        }
        .meta-title {
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }
        .download-btn {
            display: inline-block;
            background: #667eea;
            color: white;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 25px;
            margin-top: 20px;
            transition: background 0.3s;
        }
        .download-btn:hover {
            background: #5a6fd8;
        }
        .error {
            background: #ffe6e6;
            color: #d63031;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #d63031;
        }
    </style>
</head>
<body>
    <div class="story-container">
        <h1 class="story-title">❤️ Your Story ❤️</h1>
        <div class="story-content">{{ story_content }}</div>
        
        <div class="story-meta">
            <div class="meta-title">Story Details:</div>
            <p><strong>Characters:</strong> {{ name1 }} & {{ name2 }}</p>
            <p><strong>Setting:</strong> {{ setting }}</p>
            <p><strong>How they met:</strong> {{ how_met }}</p>
            <p><strong>Generated on:</strong> {{ generated_at }}</p>
        </div>
        
        <a href="/download/{{ story_id }}" class="download-btn">📥 Download PDF</a>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    """Home page with information about the service"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>✨ Story Generator</title>
        <style>
            body { 
                font-family: 'Georgia', serif; 
                max-width: 800px; 
                margin: 50px auto; 
                padding: 20px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .nav {
                background: white;
                padding: 15px 30px;
                border-radius: 15px;
                margin-bottom: 20px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .nav-brand {
                font-size: 1.5em;
                font-weight: bold;
                color: #333;
                text-decoration: none;
            }
            .nav-links {
                display: flex;
                gap: 20px;
            }
            .nav-links a {
                color: #667eea;
                text-decoration: none;
                padding: 8px 16px;
                border-radius: 20px;
                transition: all 0.3s ease;
            }
            .nav-links a:hover {
                background: #667eea;
                color: white;
            }
            .nav-links .btn-login {
                background: linear-gradient(135deg, #ff6b9d 0%, #c44569 100%);
                color: white;
            }
            .nav-links .btn-login:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(255, 107, 157, 0.3);
            }
            .container { 
                background: white; 
                padding: 40px; 
                border-radius: 20px; 
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                text-align: center;
            }
            h1 {
                color: #333;
                font-size: 2.5em;
                margin-bottom: 20px;
                font-weight: 300;
            }
            p {
                color: #666;
                font-size: 1.1em;
                line-height: 1.6;
                margin-bottom: 15px;
            }
            .features {
                display: flex;
                justify-content: space-around;
                margin: 30px 0;
                flex-wrap: wrap;
            }
            .feature {
                flex: 1;
                min-width: 200px;
                margin: 10px;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 15px;
                border-left: 4px solid #667eea;
            }
            .feature h3 {
                color: #333;
                margin-bottom: 10px;
            }
            .btn { 
                display: inline-block; 
                background: linear-gradient(135deg, #ff6b9d 0%, #c44569 100%); 
                color: white; 
                padding: 18px 40px; 
                text-decoration: none; 
                border-radius: 50px; 
                margin: 20px 10px; 
                font-size: 18px;
                font-weight: bold;
                transition: all 0.3s ease;
            }
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(255, 107, 157, 0.3);
            }
            .status {
                background: #d4edda;
                color: #155724;
                padding: 15px;
                border-radius: 10px;
                margin: 20px 0;
                border-left: 4px solid #28a745;
            }
            .content-types {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 15px;
                margin: 30px 0;
            }
            .content-type {
                background: #f8f9fa;
                padding: 15px;
                border-radius: 10px;
                border: 2px solid #e9ecef;
                transition: all 0.3s ease;
                text-decoration: none;
                color: #333;
                display: block;
            }
            .content-type:hover {
                border-color: #667eea;
                transform: translateY(-2px);
                background: #e3f2fd;
                color: #667eea;
            }
        </style>
    </head>
    <body>
        <div class="nav">
            <a href="/" class="nav-brand">✨ Story Generator</a>
            <div class="nav-links">
                <a href="/love-form">Love Stories</a>
                <a href="/universal-form">All Content</a>
                <a href="/auth/login">Login</a>
                <a href="/auth/register" class="btn-login">Sign Up</a>
            </div>
        </div>
        
        <div class="container">
            <h1>✨ Story Generator ✨</h1>
            <p>Create personalized content for any occasion - from love stories to speeches, eulogies to toasts.</p>
            <p>Share your memories and we'll craft meaningful, heartfelt content just for you.</p>
            
            <div class="status">
                <strong>✨ Ready to create your content!</strong>
                <p style="margin-top: 10px; font-size: 0.9em;">Create beautiful, personalized content for free!</p>
            </div>
            
            <div class="content-types">
                <a href="/universal-form?type=love_story" class="content-type">💕 Love Stories</a>
                <a href="/universal-form?type=wedding_speech" class="content-type">💒 Wedding Speeches</a>
                <a href="/universal-form?type=eulogy" class="content-type">🙏 Eulogies</a>
                <a href="/universal-form?type=birthday_speech" class="content-type">🎂 Birthday Speeches</a>
                <a href="/universal-form?type=anniversary_speech" class="content-type">💝 Anniversary Speeches</a>
                <a href="/universal-form?type=graduation_speech" class="content-type">🎓 Graduation Speeches</a>
                <a href="/universal-form?type=retirement_speech" class="content-type">👔 Retirement Speeches</a>
                <a href="/universal-form?type=toast" class="content-type">🥂 Toasts</a>
                <a href="/universal-form?type=tribute" class="content-type">🏆 Tributes</a>
                <a href="/universal-form?type=custom" class="content-type">✨ Custom Content</a>
            </div>
            
            <div class="features">
                <div class="feature">
                    <h3>🎨 Personalized</h3>
                    <p>Every piece is unique, crafted from your real experiences and memories.</p>
                </div>
                <div class="feature">
                    <h3>💝 Meaningful</h3>
                    <p>Beautiful, heartfelt content that captures the essence of your relationships.</p>
                </div>
                <div class="feature">
                    <h3>💾 Downloadable</h3>
                    <p>Save your content as a beautiful PDF to keep forever and share with loved ones.</p>
                </div>
            </div>
            
            <a href="/universal-form" class="btn">✨ Create Any Content</a>
            <br>
            <a href="/love-form" style="color: #667eea; text-decoration: none; font-size: 0.9em;">Just want a love story?</a>
            <br>
            <a href="/auth/register" style="color: #667eea; text-decoration: none; font-size: 0.9em;">Sign up to save your content</a>
        </div>
    </body>
    </html>
    """



@app.route('/love-form')
def love_form():
    """Serve the love story form"""
    return app.send_static_file('love_form.html')

@app.route('/universal-form')
def universal_form():
    """Serve the universal story generator form"""
    return app.send_static_file('universal_form.html')

@app.route('/webhook/tally', methods=['POST'])
def tally_webhook():
    """Handle incoming Tally form webhooks"""
    
    # Create debug log file
    import logging
    logging.basicConfig(
        filename='debug.log',
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("=== NEW WEBHOOK REQUEST ===")
        
        # Get the webhook data
        webhook_data = request.get_json()
        logger.info(f"Received webhook data: {webhook_data is not None}")
        
        if not webhook_data:
            logger.error("No webhook data received")
            return jsonify({'error': 'No data received'}), 400
        
        logger.info(f"Webhook data keys: {list(webhook_data.keys())}")
        print(f"Received Tally webhook: {json.dumps(webhook_data, indent=2)}")
        
        # Process the webhook data
        logger.info("Processing webhook data...")
        story_data = tally_handler.process_tally_webhook(webhook_data)
        logger.info(f"Processed story data: {story_data}")
        
        if not story_data:
            logger.error("Failed to process webhook data")
            return jsonify({'error': 'Failed to process webhook data'}), 400
        
        # Validate the story data
        logger.info("Validating story data...")
        if not tally_handler.validate_story_data(story_data):
            logger.error("Story data validation failed")
            return jsonify({'error': 'Missing required fields'}), 400
        
        logger.info("Story data validated successfully")
        
        # Generate the story using ChatGPT
        logger.info("Starting story generation...")
        story_text = story_generator.generate_story(story_data)
        logger.info(f"Story generation result: {story_text is not None}")
        
        if not story_text:
            logger.error("Failed to generate story")
            return jsonify({'error': 'Failed to generate story'}), 500
        
        logger.info("Story generated successfully")
        
        # Save the submission and story
        logger.info("Saving submission...")
        filename = tally_handler.save_submission(story_data, story_text)
        logger.info(f"Saved to file: {filename}")
        
        # Create a unique story ID for the URL
        story_id = story_data.get('submission_id', '')[:8]
        if not story_id:
            from datetime import datetime
            story_id = datetime.now().strftime("%Y%m%d%H%M")
        
        # Clean the story ID to remove any special characters
        import re
        story_id = re.sub(r'[^a-zA-Z0-9]', '', story_id)
        if not story_id:
            story_id = 'story_' + datetime.now().strftime("%Y%m%d%H%M")
        
        logger.info(f"Created story ID: {story_id}")
        
        # Store the story temporarily (in production, use a database)
        story_storage[story_id] = {
            'story_text': story_text,
            'story_data': story_data,
            'filename': filename
        }
        
        logger.info("Story stored in memory successfully")
        
        # Return success response
        response_data = {
            'success': True,
            'message': 'Story generated successfully',
            'story_url': f'/story/{story_id}',
            'download_url': f'/download/{story_id}'
        }
        logger.info(f"Returning success response: {response_data}")
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Exception occurred: {str(e)}", exc_info=True)
        print(f"Error processing webhook: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/webhook/universal', methods=['POST'])
def universal_webhook():
    """Handle universal form submissions"""
    
    # Create debug log file
    import logging
    logging.basicConfig(
        filename='debug.log',
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("=== NEW UNIVERSAL WEBHOOK REQUEST ===")
        
        # Get the webhook data
        webhook_data = request.get_json()
        logger.info(f"Received universal webhook data: {webhook_data is not None}")
        
        if not webhook_data:
            logger.error("No webhook data received")
            return jsonify({'error': 'No data received'}), 400
        
        logger.info(f"Universal webhook data keys: {list(webhook_data.keys())}")
        print(f"Received universal webhook: {json.dumps(webhook_data, indent=2)}")
        
        # Extract form data from webhook
        form_data = {}
        try:
            answers = webhook_data['eventBody']['event']['formResponses'][0]['answers']
            for answer in answers:
                form_data[answer['fieldId']] = answer['value']
        except (KeyError, IndexError) as e:
            logger.error(f"Failed to extract form data: {e}")
            return jsonify({'error': 'Invalid form data format'}), 400
        
        logger.info(f"Extracted form data: {form_data}")
        
        # Validate required fields
        required_fields = ['content_type', 'tone', 'speaker_name', 'recipient_name', 'relationship', 'occasion', 'key_memories', 'traits', 'length']
        missing_fields = [field for field in required_fields if not form_data.get(field)]
        
        if missing_fields:
            logger.error(f"Missing required fields: {missing_fields}")
            return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400
        
        logger.info("Form data validated successfully")
        
        # Generate content using universal generator
        logger.info("Starting content generation...")
        content_text = universal_generator.generate_content(form_data)
        logger.info(f"Content generation result: {content_text is not None}")
        
        if not content_text:
            logger.error("Failed to generate content")
            return jsonify({'error': 'Failed to generate content'}), 500
        
        logger.info("Content generated successfully")
        
        # Create a unique content ID for the URL
        from datetime import datetime
        import re
        content_id = f"content_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        logger.info(f"Created content ID: {content_id}")
        
        # Store the content temporarily (in production, use a database)
        story_storage[content_id] = {
            'story_text': content_text,
            'story_data': form_data,
            'filename': f'universal_{content_id}.json'
        }
        
        logger.info("Content stored in memory successfully")
        
        # Return success response
        response_data = {
            'success': True,
            'message': 'Content generated successfully',
            'story_url': f'/story/{content_id}',
            'download_url': f'/download/{content_id}'
        }
        logger.info(f"Returning success response: {response_data}")
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Exception occurred: {str(e)}", exc_info=True)
        print(f"Error processing universal webhook: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/story/<story_id>')
def display_story(story_id):
    """Display the generated story"""
    
    # First check in-memory storage
    if story_id in story_storage:
        story_info = story_storage[story_id]
        story_text = story_info['story_text']
        story_data = story_info['story_data']
    else:
        # Try to load from saved file
        import json
        import os
        import glob
        
        # Look for saved files
        saved_files = glob.glob('data/submission_*.json')
        for file_path in saved_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    saved_data = json.load(f)
                    if saved_data.get('submission_data', {}).get('submission_id', '').startswith(story_id):
                        story_text = saved_data.get('story_text', 'Story not found')
                        story_data = saved_data.get('submission_data', {})
                        break
            except:
                continue
        else:
            return "Story not found", 404
    
    return render_template_string(STORY_TEMPLATE,
        story_content=story_text,
        name1=story_data.get('name1', 'Unknown'),
        name2=story_data.get('name2', 'Unknown'),
        setting=story_data.get('setting', 'Unknown'),
        how_met=story_data.get('how_met', 'Unknown'),
        generated_at=story_data.get('submitted_at', 'Unknown'),
        story_id=story_id
    )

@app.route('/download/<story_id>')
def download_story(story_id):
    """Download the story as a beautiful PDF file"""
    
    if story_id not in story_storage:
        return "Story not found", 404
    
    story_info = story_storage[story_id]
    story_text = story_info['story_text']
    story_data = story_info['story_data']
    
    # Check if PDF generation is available
    if not PDF_AVAILABLE:
        # Fallback to text file if PDF generation is not available
        from flask import Response
        download_content = f"""TOLD WITH LOVE

Characters: {story_data.get('name1', 'Unknown')} & {story_data.get('name2', 'Unknown')}
How they met: {story_data.get('how_met', 'Unknown')}
Favorite memory: {story_data.get('favorite_memory', 'Unknown')}
Generated: {datetime.datetime.now().strftime('%B %d, %Y at %I:%M %p')}

{story_text}

---
This love story was created with love by Told with Love
Generated on {datetime.datetime.now().strftime('%B %d, %Y')}
Story ID: {story_id}
"""
        response = Response(download_content, mimetype='text/plain')
        response.headers['Content-Disposition'] = f'attachment; filename=told_with_love_{story_id}.txt'
        return response
    
    # Generate beautiful PDF with enhanced design
    
    # Create PDF in memory
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    
    # Create story elements
    story_elements = []
    
    # Custom styles with better fonts and colors
    styles = getSampleStyleSheet()
    
    # Enhanced title style with decorative elements
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=36,
        spaceAfter=40,
        alignment=TA_CENTER,
        textColor=safe_color('#e91e63') or Color(0.91, 0.12, 0.39),  # Bright pink
        fontName='Helvetica-Bold',
        leading=40
    )
    
    # Subtitle style for story details
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=25,
        alignment=TA_CENTER,
        textColor=safe_color('#3f51b5') or Color(0.25, 0.32, 0.71),  # Indigo
        fontName='Helvetica-Bold',
        leading=20
    )
    
    # Enhanced story text style with better readability
    story_style = ParagraphStyle(
        'CustomStory',
        parent=styles['Normal'],
        fontSize=13,
        spaceAfter=16,
        alignment=TA_JUSTIFY,
        textColor=safe_color('#2c3e50') or Color(0.17, 0.24, 0.31),  # Dark blue-gray
        fontName='Helvetica',
        leading=20,
        firstLineIndent=20
    )
    
    # Meta info style for story details
    meta_style = ParagraphStyle(
        'CustomMeta',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=10,
        alignment=TA_LEFT,
        textColor=safe_color('#7f8c8d') or Color(0.50, 0.55, 0.55),  # Gray
        fontName='Helvetica'
    )
    
    # Decorative header with proper heart symbols
    header_text = "♥ Your Love Story ♥"
    story_elements.append(Paragraph(header_text, title_style))
    story_elements.append(Spacer(1, 20))
    
    # Extract the creative title from the story (first line)
    story_lines = story_text.split('\n')
    creative_title = story_lines[0].strip() if story_lines else "A Love Story"
    # Clean up any markdown formatting (asterisks, etc.)
    creative_title = creative_title.replace('*', '').replace('**', '').strip()
    
    # Display the creative title
    story_elements.append(Paragraph(creative_title, subtitle_style))
    story_elements.append(Spacer(1, 30))

    # Add decorative separator
    separator_style = ParagraphStyle(
        'Separator',
        parent=styles['Normal'],
        fontSize=16,
        alignment=TA_CENTER,
        textColor=safe_color('#e91e63') or Color(0.91, 0.12, 0.39),
        spaceAfter=20,
        spaceBefore=20
    )
    story_elements.append(Paragraph("♥ ♥ ♥", separator_style))
    story_elements.append(Spacer(1, 20))

    # Add the full story text with proper heart symbol handling (skip the first line which is the title)
    story_lines = story_text.split('\n')
    story_content = '\n'.join(story_lines[1:])  # Skip the first line (title)
    
    paragraphs = story_content.split('\n\n')
    for paragraph in paragraphs:
        if paragraph.strip():
            # Clean up markdown and replace heart symbols properly
            clean_paragraph = paragraph.strip().replace('**', '').replace('💕', '♥').replace('❤️', '♥').replace('💖', '♥')
            story_elements.append(Paragraph(clean_paragraph, story_style))
            story_elements.append(Spacer(1, 16))
    
    # Add footer with decorative elements
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        textColor=safe_color('#6c757d') or Color(0.42, 0.46, 0.49),
        spaceBefore=30
    )
    
    footer_text = f"♥ Generated with love on {datetime.datetime.now().strftime('%B %d, %Y')} ♥"
    story_elements.append(Paragraph(footer_text, footer_style))
    
    # Build PDF
    def add_loving_background(canvas, doc):
        canvas.saveState()
        # Very light pink background that won't interfere with text
        canvas.setFillColor(safe_color('#fef7f9') or Color(0.996, 0.969, 0.976))
        canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
        canvas.restoreState()

    doc.build(story_elements, onFirstPage=add_loving_background, onLaterPages=add_loving_background)
    
    # Get PDF content
    pdf_content = buffer.getvalue()
    buffer.close()
    
    # Create response
    from flask import Response
    response = Response(pdf_content, mimetype='application/pdf')
    response.headers['Content-Disposition'] = f'attachment; filename=told_with_love_{story_id}.pdf'
    return response

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'love_story_generator'})

@app.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events"""
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature', '')
    
    payment_processor = PaymentProcessor()
    
    if payment_processor.handle_webhook(payload, sig_header):
        return jsonify({'status': 'success'}), 200
    else:
        return jsonify({'status': 'error'}), 400

# In-memory storage for stories (use a database in production)
story_storage = {}

if __name__ == '__main__':
    print("Starting Love Story Generator Web Server...")
    print("Webhook endpoint: http://localhost:3000/webhook/tally")
    print("Health check: http://localhost:3000/health")
    
    # Create database tables
    with app.app_context():
        db.create_all()
        print("Database initialized")
    
    # Get port from environment variable (Railway sets this)
    port = int(os.environ.get('PORT', 3000))
    
    # Run in production mode on Railway
    app.run(debug=False, host='0.0.0.0', port=port) 