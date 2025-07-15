# Tally Form Integration Setup Guide

This guide will help you integrate your Tally form with the Love Story Generator to automatically create personalized love stories using ChatGPT.

## 🚀 Quick Start

### 1. Start the Web Server

```bash
# Activate your virtual environment
source venv/bin/activate

# Start the web server
python web_server.py
```

The server will start at `http://localhost:5000`

### 2. Test the Integration

1. Visit `http://localhost:5000/test-form` to test the form locally
2. Fill out the form and submit to generate a story
3. View and download your generated story

## 📋 Setting Up Your Tally Form

### Step 1: Create Your Tally Form

1. Go to [Tally](https://tally.so) and create a new form
2. Add the following fields to your form:

| Field Type | Field Name              | Internal Key      | Required |
| ---------- | ----------------------- | ----------------- | -------- |
| Short text | First Character's Name  | `name1`           | ✅       |
| Short text | Second Character's Name | `name2`           | ✅       |
| Short text | Story Setting           | `setting`         | ✅       |
| Short text | How They Met            | `how_met`         | ✅       |
| Short text | Shared Interest         | `shared_interest` | ✅       |
| Short text | Challenge/Obstacle      | `challenge`       | ✅       |
| Long text  | What Makes It Special   | `special_thing`   | ✅       |
| Dropdown   | Story Length            | `story_length`    | ✅       |

### Step 2: Configure Webhook

1. In your Tally form, go to **Settings** → **Integrations**
2. Click **Add integration** → **Webhook**
3. Set the webhook URL to: `https://your-domain.com/webhook/tally`
4. Set the trigger to: **Form submission**
5. Save the integration

### Step 3: Map Your Form Fields

You'll need to update the field mapping in `src/tally_handler.py` to match your Tally form field IDs.

1. Submit a test form in Tally
2. Check the webhook payload in your server logs
3. Update the `form_fields_mapping` in `TallyHandler` class:

```python
self.form_fields_mapping = {
    'name1': ['your_tally_field_id_1'],
    'name2': ['your_tally_field_id_2'],
    'setting': ['your_tally_field_id_3'],
    # ... etc
}
```

## 🌐 Deploying to Production

### Option 1: Local Development with ngrok

For testing with Tally webhooks:

```bash
# Install ngrok
brew install ngrok  # macOS
# or download from https://ngrok.com

# Start your web server
python web_server.py

# In another terminal, expose your local server
ngrok http 5000
```

Use the ngrok URL (e.g., `https://abc123.ngrok.io`) as your Tally webhook URL.

### Option 2: Deploy to a Cloud Service

#### Heroku

```bash
# Create Procfile
echo "web: python web_server.py" > Procfile

# Deploy
heroku create your-love-story-generator
git add .
git commit -m "Add web server"
git push heroku main
```

#### Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway login
railway init
railway up
```

#### DigitalOcean App Platform

1. Connect your GitHub repository
2. Set build command: `pip install -r requirements.txt`
3. Set run command: `python web_server.py`
4. Add environment variables for your OpenAI API key

## 🔧 Configuration

### Environment Variables

Create a `.env` file with:

```env
OPENAI_API_KEY=your_openai_api_key_here
FLASK_ENV=production
FLASK_SECRET_KEY=your_secret_key_here
```

### Production Settings

For production deployment, update `web_server.py`:

```python
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
```

## 📊 Monitoring and Logs

### Health Check

Visit `/health` to check if your service is running:

```json
{
  "status": "healthy",
  "service": "love_story_generator"
}
```

### View Generated Stories

- Stories are saved in the `data/` directory
- Each submission creates a JSON file with form data and generated story
- Stories are also stored temporarily in memory for web viewing

## 🐛 Troubleshooting

### Common Issues

1. **Webhook not receiving data**

   - Check your webhook URL is correct
   - Ensure your server is accessible from the internet
   - Check server logs for incoming requests

2. **Story generation fails**

   - Verify your OpenAI API key is valid
   - Check API usage limits
   - Review the form data mapping

3. **Field mapping issues**
   - Submit a test form and check the webhook payload
   - Update the field mapping in `TallyHandler`
   - Use the test form to verify the mapping works

### Debug Mode

Enable debug logging by setting:

```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

## 📝 Customization

### Adding New Fields

1. Add the field to your Tally form
2. Update the `form_fields_mapping` in `TallyHandler`
3. Update the `defaults` dictionary
4. Modify the story prompt in `StoryGenerator.create_prompt()`

### Customizing the Story Template

Edit the `STORY_TEMPLATE` in `web_server.py` to change the story display format.

### Adding Email Notifications

You can extend the webhook handler to send email notifications when stories are generated.

## 🔒 Security Considerations

1. **API Key Security**: Never commit your OpenAI API key to version control
2. **Webhook Validation**: Consider adding webhook signature validation
3. **Rate Limiting**: Implement rate limiting for the webhook endpoint
4. **Input Validation**: Validate all form inputs before processing

## 📈 Scaling

For high-volume usage:

1. **Database**: Replace in-memory storage with a database (PostgreSQL, MongoDB)
2. **Queue System**: Use Redis/Celery for background story generation
3. **Caching**: Cache generated stories to avoid regenerating similar requests
4. **Load Balancing**: Use multiple server instances behind a load balancer

## 🎯 Next Steps

1. Set up your Tally form with the required fields
2. Deploy your web server to a cloud service
3. Configure the webhook URL in Tally
4. Test the integration with a few submissions
5. Monitor and optimize based on usage

Your Love Story Generator is now ready to receive Tally form submissions and generate personalized stories using ChatGPT! 🎉
