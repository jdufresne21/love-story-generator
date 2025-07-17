# Stripe Setup Guide

## Your Stripe Test Key

You have provided your Stripe test secret key. For security reasons, it's not shown in this documentation.

## Next Steps to Complete Stripe Setup

### 1. Get Your Stripe Publishable Key

1. Go to https://dashboard.stripe.com/apikeys
2. Copy your **Publishable key** (starts with `pk_test_`)
3. Add it to your environment variables as `STRIPE_PUBLISHABLE_KEY`

### 2. Create Subscription Products

1. Go to https://dashboard.stripe.com/products
2. Create 3 products:
   - **Basic Plan** ($4.99/month)
   - **Premium Plan** ($9.99/month)
   - **Pro Plan** ($19.99/month)
3. Copy the **Price IDs** (start with `price_`)
4. Add them to your environment variables:
   - `STRIPE_BASIC_PRICE_ID`
   - `STRIPE_PREMIUM_PRICE_ID`
   - `STRIPE_PRO_PRICE_ID`

### 3. Set Up Webhook Endpoint

1. Go to https://dashboard.stripe.com/webhooks
2. Click "Add endpoint"
3. Set endpoint URL to: `https://yourdomain.com/webhook/stripe`
4. Select these events:
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
5. Copy the **Webhook signing secret** (starts with `whsec_`)
6. Add it to your environment variables as `STRIPE_WEBHOOK_SECRET`

### 4. Environment Variables Summary

```bash
# You need to add these:
STRIPE_SECRET_KEY=your_stripe_secret_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
STRIPE_BASIC_PRICE_ID=price_your_basic_plan_id_here
STRIPE_PREMIUM_PRICE_ID=price_your_premium_plan_id_here
STRIPE_PRO_PRICE_ID=price_your_pro_plan_id_here
```

### 5. Quick Setup Script

Run this to set up all environment variables:

```bash
python3 setup_env.py
```

### 6. Test Your Setup

1. Start your application: `python web_server.py`
2. Go to the upgrade page: `/auth/upgrade`
3. Test with Stripe's test card: `4242 4242 4242 4242`

## Production vs Test Keys

- **Test keys** (current): Start with `sk_test_` and `pk_test_`
- **Live keys**: Start with `sk_live_` and `pk_live_`
- Switch to live keys when you're ready to accept real payments
