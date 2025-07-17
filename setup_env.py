#!/usr/bin/env python3
"""
Environment Variables Setup Script
Helps configure environment variables for the Love Story Generator
"""

import os
import secrets
import sys

def generate_secret_key():
    """Generate a secure secret key"""
    return secrets.token_hex(32)

def create_env_file():
    """Create .env file with user input"""
    
    print("🔧 Love Story Generator - Environment Setup")
    print("=" * 50)
    
    # Get OpenAI API Key
    print("\n1. OpenAI API Key")
    print("   Get your API key from: https://platform.openai.com/api-keys")
    openai_key = input("   Enter your OpenAI API key (starts with 'sk-'): ").strip()
    
    if not openai_key.startswith('sk-'):
        print("   ⚠️  Warning: OpenAI API key should start with 'sk-'")
    
    # Get Stripe Keys
    print("\n2. Stripe Configuration")
    print("   Get your keys from: https://dashboard.stripe.com/apikeys")
    
    stripe_secret = input("   Enter your Stripe Secret Key (starts with 'sk_test_' or 'sk_live_'): ").strip()
    stripe_publishable = input("   Enter your Stripe Publishable Key (starts with 'pk_test_' or 'pk_live_'): ").strip()
    
    # Get Stripe Price IDs
    print("\n3. Stripe Price IDs")
    print("   Create products in: https://dashboard.stripe.com/products")
    print("   Then copy the price IDs (start with 'price_')")
    
    basic_price = input("   Enter Basic Plan Price ID: ").strip()
    premium_price = input("   Enter Premium Plan Price ID: ").strip()
    pro_price = input("   Enter Pro Plan Price ID: ").strip()
    
    # Get Base URL
    print("\n4. Application URL")
    base_url = input("   Enter your app's base URL (local: http://localhost:3000, production: https://yourdomain.com): ").strip()
    if not base_url:
        base_url = "http://localhost:3000"
    
    # Generate secret key
    secret_key = generate_secret_key()
    
    # Create .env content
    env_content = f"""# Environment Variables for Love Story Generator
# Generated automatically - DO NOT commit this file to version control

# OpenAI Configuration
OPENAI_API_KEY={openai_key}

# Database Configuration
DATABASE_URL=sqlite:///love_stories.db

# Flask Security
SECRET_KEY={secret_key}

# Base URL for the application
BASE_URL={base_url}

# Stripe Configuration (for payments)
STRIPE_SECRET_KEY={stripe_secret}
STRIPE_PUBLISHABLE_KEY={stripe_publishable}
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret_here

# Stripe Price IDs
STRIPE_BASIC_PRICE_ID={basic_price}
STRIPE_PREMIUM_PRICE_ID={premium_price}
STRIPE_PRO_PRICE_ID={pro_price}

# Tally Configuration (optional - for form integration)
TALLY_API_URL=your_tally_api_url_here
TALLY_API_KEY=your_tally_api_key_here
"""
    
    # Write to .env file
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print(f"\n✅ Successfully created .env file!")
        print(f"   Secret Key generated: {secret_key[:20]}...")
        
        print("\n📋 Next Steps:")
        print("   1. Set up Stripe webhook endpoint")
        print("   2. Get your Stripe webhook secret")
        print("   3. Update STRIPE_WEBHOOK_SECRET in .env")
        print("   4. Test your application: python web_server.py")
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False
    
    return True

def main():
    """Main function"""
    if os.path.exists('.env'):
        response = input("⚠️  .env file already exists. Overwrite? (y/N): ").strip().lower()
        if response != 'y':
            print("Setup cancelled.")
            return
    
    if create_env_file():
        print("\n🎉 Environment setup complete!")
    else:
        print("\n❌ Setup failed. Please try again.")

if __name__ == "__main__":
    main() 