#!/usr/bin/env python3
"""
Web Server for Love Story Generator - Handles Tally form webhooks
"""

from flask import Flask, request, jsonify, render_template_string
import json
import os
import sys
import datetime
from io import BytesIO
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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
from src.tally_handler import TallyHandler
from config.settings import Config

app = Flask(__name__, static_folder='static')

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
        <title>Told with Love</title>
        <style>
            body { 
                font-family: 'Georgia', serif; 
                max-width: 800px; 
                margin: 50px auto; 
                padding: 20px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
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
        </style>
    </head>
    <body>
        <div class="container">
            <h1>❤️ Told with Love ❤️</h1>
            <p>Create beautiful, personalized love stories that capture your unique romance.</p>
            <p>Share your special moments and we'll craft a magical narrative just for you and your partner.</p>
            
            <div class="status">
                <strong>✨ Ready to create your love story!</strong>
            </div>
            
            <div class="features">
                <div class="feature">
                    <h3>🎨 Personalized</h3>
                    <p>Every story is unique, crafted from your real experiences and memories.</p>
                </div>
                <div class="feature">
                    <h3>💝 Romantic</h3>
                    <p>Beautiful, heartwarming stories that celebrate your love and connection.</p>
                </div>
                <div class="feature">
                    <h3>💾 Downloadable</h3>
                    <p>Save your story as a beautiful PDF to keep forever and share with loved ones.</p>
                </div>
            </div>
            
            <a href="/love-form" class="btn">❤️ Create Your Story</a>
        </div>
    </body>
    </html>
    """



@app.route('/love-form')
def love_form():
    """Serve the love story form"""
    return app.send_static_file('love_form.html')

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
        fontSize=28,
        spaceAfter=40,
        alignment=TA_CENTER,
        textColor=safe_color('#e91e63') or Color(0.91, 0.12, 0.39),  # Bright pink
        fontName='Helvetica-Bold',
        leading=32
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

    # Add the full story text with proper heart symbol handling
    paragraphs = story_text.split('\n\n')
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
        # Soft pink background
        canvas.setFillColor(safe_color('#ffe6f2') or Color(1, 0.9, 0.95))
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

# In-memory storage for stories (use a database in production)
story_storage = {}

if __name__ == '__main__':
    print("Starting Love Story Generator Web Server...")
    print("Webhook endpoint: http://localhost:3000/webhook/tally")
    print("Health check: http://localhost:3000/health")
    
    # Get port from environment variable (Railway sets this)
    port = int(os.environ.get('PORT', 3000))
    
    # Run in production mode on Railway
    app.run(debug=False, host='0.0.0.0', port=port) 