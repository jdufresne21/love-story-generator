"""
Payment Processing Module - Handles Stripe integration for subscriptions
"""

import stripe
import os
from datetime import datetime, timedelta
from typing import Dict, Optional
from src.user_models import db, User

# Initialize Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

class PaymentProcessor:
    """Handles payment processing and subscription management"""
    
    def __init__(self):
        """Initialize the payment processor"""
        self.plans = {
            'basic': {
                'name': 'Basic Plan',
                'price_id': os.environ.get('STRIPE_BASIC_PRICE_ID'),
                'stories_per_month': 3,
                'price': 4.99,
                'features': ['3 stories per month', 'High-quality PDFs', 'Story history']
            },
            'premium': {
                'name': 'Premium Plan',
                'price_id': os.environ.get('STRIPE_PREMIUM_PRICE_ID'),
                'stories_per_month': 10,
                'price': 9.99,
                'features': ['10 stories per month', 'Premium PDF themes', 'Priority support', 'Story sharing']
            },
            'pro': {
                'name': 'Pro Plan',
                'price_id': os.environ.get('STRIPE_PRO_PRICE_ID'),
                'stories_per_month': -1,  # Unlimited
                'price': 19.99,
                'features': ['Unlimited stories', 'All premium themes', 'API access', 'Bulk generation', 'White-label options']
            }
        }
    
    def create_checkout_session(self, user: User, plan_type: str) -> Optional[str]:
        """Create a Stripe checkout session for subscription"""
        try:
            if plan_type not in self.plans:
                raise ValueError(f"Invalid plan type: {plan_type}")
            
            plan = self.plans[plan_type]
            
            checkout_session = stripe.checkout.Session.create(
                customer_email=user.email,
                line_items=[{
                    'price': plan['price_id'],
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=f"{os.environ.get('BASE_URL', 'http://localhost:3000')}/auth/payment/success?session_id={{CHECKOUT_SESSION_ID}}",
                cancel_url=f"{os.environ.get('BASE_URL', 'http://localhost:3000')}/auth/payment/cancel",
                metadata={
                    'user_id': user.id,
                    'plan_type': plan_type
                }
            )
            
            return checkout_session.id
            
        except Exception as e:
            print(f"Error creating checkout session: {e}")
            return None
    
    def handle_webhook(self, payload: bytes, sig_header: str) -> bool:
        """Handle Stripe webhook events"""
        try:
            webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
            
            if event['type'] == 'checkout.session.completed':
                self._handle_checkout_completed(event['data']['object'])
            elif event['type'] == 'customer.subscription.updated':
                self._handle_subscription_updated(event['data']['object'])
            elif event['type'] == 'customer.subscription.deleted':
                self._handle_subscription_cancelled(event['data']['object'])
            
            return True
            
        except Exception as e:
            print(f"Error handling webhook: {e}")
            return False
    
    def _handle_checkout_completed(self, session):
        """Handle successful checkout completion"""
        try:
            user_id = session['metadata']['user_id']
            plan_type = session['metadata']['plan_type']
            
            user = User.query.get(user_id)
            if user:
                user.plan_type = plan_type
                user.plan_start_date = datetime.utcnow()
                user.plan_end_date = datetime.utcnow() + timedelta(days=30)
                user.stripe_customer_id = session.get('customer')
                user.stripe_subscription_id = session.get('subscription')
                
                db.session.commit()
                print(f"User {user.username} upgraded to {plan_type} plan")
                
        except Exception as e:
            print(f"Error handling checkout completion: {e}")
    
    def _handle_subscription_updated(self, subscription):
        """Handle subscription updates"""
        try:
            user = User.query.filter_by(stripe_subscription_id=subscription['id']).first()
            if user:
                # Update subscription status
                if subscription['status'] == 'active':
                    user.plan_end_date = datetime.fromtimestamp(subscription['current_period_end'])
                db.session.commit()
                
        except Exception as e:
            print(f"Error handling subscription update: {e}")
    
    def _handle_subscription_cancelled(self, subscription):
        """Handle subscription cancellation"""
        try:
            user = User.query.filter_by(stripe_subscription_id=subscription['id']).first()
            if user:
                user.plan_type = 'free'
                user.plan_end_date = None
                db.session.commit()
                print(f"User {user.username} subscription cancelled")
                
        except Exception as e:
            print(f"Error handling subscription cancellation: {e}")
    
    def get_plans(self) -> Dict:
        """Get available subscription plans"""
        return self.plans
    
    def cancel_subscription(self, user: User) -> bool:
        """Cancel user's subscription"""
        try:
            if user.stripe_subscription_id:
                stripe.Subscription.modify(
                    user.stripe_subscription_id,
                    cancel_at_period_end=True
                )
                return True
        except Exception as e:
            print(f"Error cancelling subscription: {e}")
        return False
    
    def create_portal_session(self, user: User) -> Optional[str]:
        """Create Stripe customer portal session"""
        try:
            if user.stripe_customer_id:
                session = stripe.billing_portal.Session.create(
                    customer=user.stripe_customer_id,
                    return_url=f"{os.environ.get('BASE_URL', 'http://localhost:3000')}/account"
                )
                return session.url
        except Exception as e:
            print(f"Error creating portal session: {e}")
        return None 