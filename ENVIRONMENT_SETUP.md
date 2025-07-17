# Environment Variables Setup Guide

This guide explains how to set up environment variables for your Love Story Generator project.

## Required Environment Variables

### 1. **Local Development Setup**

Create a `.env` file in your project root directory:

```bash
# Copy the template
cp env_template.txt .env

# Edit the .env file with your actual values
nano .env
```

### 2. **Environment Variables Explained**

#### **OpenAI Configuration**

- `OPENAI_API_KEY`: Your OpenAI API key (required for story generation)
  - Get this from: https://platform.openai.com/api-keys
  - Format: `sk-...`

#### **Database Configuration**

- `DATABASE_URL`: Database connection string
  - Local: `sqlite:///love_stories.db`
  - Production: Your database URL (e.g., PostgreSQL)

#### **Flask Security**

- `SECRET_KEY`: Secret key for Flask sessions
  - Generate a secure random string
  - Example: `python -c "import secrets; print(secrets.token_hex(32))"`

#### **Application URL**

- `BASE_URL`: Your application's base URL
  - Local: `http://localhost:3000`
  - Production: `https://yourdomain.com`

#### **Stripe Configuration (for payments)**

- `STRIPE_SECRET_KEY`: Your Stripe secret key
- `STRIPE_PUBLISHABLE_KEY`: Your Stripe publishable key
- `STRIPE_WEBHOOK_SECRET`: Webhook endpoint secret
- `STRIPE_BASIC_PRICE_ID`: Price ID for Basic plan
- `STRIPE_PREMIUM_PRICE_ID`: Price ID for Premium plan
- `STRIPE_PRO_PRICE_ID`: Price ID for Pro plan

#### **Tally Configuration (optional)**

- `TALLY_API_URL`: Tally form API URL
- `TALLY_API_KEY`: Tally API key

## 3. **Production Deployment Setup**

### **Railway Deployment**

If you're deploying to Railway, set environment variables in the Railway dashboard:

1. Go to your Railway project dashboard
2. Navigate to "Variables" tab
3. Add each environment variable with its value

### **Other Platforms**

For other deployment platforms (Heroku, DigitalOcean, etc.), set environment variables in their respective dashboards.

## 4. **Getting API Keys**

### **OpenAI API Key**

1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Copy the key (starts with `sk-`)

### **Stripe Keys**

1. Go to https://dashboard.stripe.com/apikeys
2. Copy your publishable and secret keys
3. Create webhook endpoints for payment processing

### **Stripe Price IDs**

1. Go to https://dashboard.stripe.com/products
2. Create products for each subscription tier
3. Copy the price IDs (start with `price_`)

## 5. **Security Best Practices**

1. **Never commit `.env` files to version control**
2. **Use strong, unique secret keys**
3. **Rotate API keys regularly**
4. **Use environment-specific configurations**

## 6. **Testing Your Setup**

After setting up environment variables, test your configuration:

```bash
# Start the development server
python web_server.py

# Check if all required variables are loaded
python -c "from config.settings import Config; c = Config(); print('Configuration loaded successfully')"
```

## 7. **Troubleshooting**

### **Common Issues**

- **Missing OpenAI API Key**: Story generation won't work
- **Invalid Stripe Keys**: Payment processing will fail
- **Missing Secret Key**: Flask sessions won't work properly

### **Debug Mode**

Enable debug mode to see detailed error messages:

```python
# In web_server.py, add:
app.debug = True
```

## 8. **Environment Variable Priority**

The application loads environment variables in this order:

1. System environment variables
2. `.env` file (local development)
3. Default values (if any)

## 9. **Next Steps**

After setting up environment variables:

1. Test the application locally
2. Set up Stripe products and webhooks
3. Deploy to your chosen platform
4. Configure production environment variables
