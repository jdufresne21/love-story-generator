# Stripe Webhook Setup Guide

## 🎯 Overview

Webhooks are essential for handling payment events like successful subscriptions, cancellations, and updates in real-time.

## 📋 Required Events

Your webhook needs to handle these events:

- `checkout.session.completed` - When a customer completes a purchase
- `customer.subscription.updated` - When a subscription is modified
- `customer.subscription.deleted` - When a subscription is cancelled
- `invoice.payment_succeeded` - When a payment succeeds
- `invoice.payment_failed` - When a payment fails

## 🚀 Setup Steps

### **Step 1: Create Webhook Endpoint**

1. **Go to**: https://dashboard.stripe.com/webhooks
2. **Click "Add endpoint"**
3. **Set endpoint URL**:
   - **Production**: `https://your-app-name.railway.app/webhook/stripe`
   - **Local Testing**: `http://localhost:3000/webhook/stripe` (requires ngrok)
4. **Select events** (check all the ones listed above)
5. **Click "Add endpoint"**

### **Step 2: Get Webhook Secret**

After creating the endpoint, you'll see a **Webhook signing secret** that starts with `whsec_`. Copy this secret.

### **Step 3: Update Environment Variables**

Add the webhook secret to your `.env` file:

```bash
STRIPE_WEBHOOK_SECRET=whsec_your_actual_webhook_secret_here
```

### **Step 4: Test the Webhook**

#### **Option A: Production Testing (Recommended)**

1. Deploy your app to Railway
2. Use the production URL in your webhook endpoint
3. Test with Stripe's test mode

#### **Option B: Local Testing (Advanced)**

1. Install ngrok: `brew install ngrok/ngrok/ngrok`
2. Sign up for free ngrok account: https://ngrok.com
3. Authenticate: `ngrok config add-authtoken YOUR_TOKEN`
4. Expose local server: `ngrok http 3000`
5. Use the ngrok URL in your webhook endpoint

## 🔧 Webhook Endpoint Code

Your webhook endpoint is already implemented in `web_server.py`:

```python
@app.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.environ.get('STRIPE_WEBHOOK_SECRET')
        )

        if event['type'] == 'checkout.session.completed':
            # Handle successful checkout
            pass
        elif event['type'] == 'customer.subscription.updated':
            # Handle subscription updates
            pass
        elif event['type'] == 'customer.subscription.deleted':
            # Handle subscription cancellations
            pass

        return jsonify({'status': 'success'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400
```

## 🧪 Testing Your Webhook

### **Test Events in Stripe Dashboard**

1. Go to your webhook endpoint in Stripe
2. Click "Send test webhook"
3. Select an event type (e.g., `checkout.session.completed`)
4. Click "Send test webhook"
5. Check your application logs for the event

### **Test with Real Payments**

1. Use Stripe's test card: `4242 4242 4242 4242`
2. Complete a test purchase
3. Check your webhook logs in Stripe dashboard
4. Verify the event was processed in your app

## 📊 Monitoring Webhooks

### **Stripe Dashboard**

- Go to https://dashboard.stripe.com/webhooks
- Click on your webhook endpoint
- View "Recent deliveries" for success/failure rates

### **Application Logs**

Your application logs webhook events. Check for:

- Successful event processing
- Error messages
- Database updates

## 🚨 Troubleshooting

### **Common Issues**

1. **Webhook not receiving events**: Check endpoint URL is correct
2. **Signature verification failed**: Verify webhook secret is correct
3. **404 errors**: Ensure your app is running and accessible
4. **500 errors**: Check your application logs for errors

### **Debug Mode**

Enable debug logging in your application:

```python
app.debug = True
```

## 🔒 Security Best Practices

1. **Always verify webhook signatures** (already implemented)
2. **Use HTTPS in production** (Railway provides this)
3. **Keep webhook secrets secure** (use environment variables)
4. **Monitor webhook failures** (check Stripe dashboard regularly)

## 📈 Production Checklist

- [ ] Webhook endpoint created in Stripe
- [ ] All required events selected
- [ ] Webhook secret added to environment variables
- [ ] Application deployed and accessible
- [ ] Webhook tested with test events
- [ ] Webhook tested with real test payments
- [ ] Monitoring set up for webhook failures

## 🎉 Next Steps

Once your webhook is set up:

1. **Test thoroughly** with Stripe's test mode
2. **Monitor webhook delivery** in Stripe dashboard
3. **Set up alerts** for webhook failures
4. **Go live** when ready to accept real payments
