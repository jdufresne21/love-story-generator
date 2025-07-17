"""
Authentication Module - Handles user login, registration, and account management
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from src.user_models import db, User, Story
from src.payments import PaymentProcessor
import re

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not username or not email or not password:
            flash('All fields are required', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'error')
            return render_template('register.html')
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('register.html')
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Please enter both username and password', 'error')
            return render_template('login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('home'))

@auth.route('/account')
@login_required
def account():
    """User account dashboard"""
    user = current_user
    stories = Story.query.filter_by(user_id=user.id).order_by(Story.created_at.desc()).limit(5).all()
    
    return render_template('account.html', user=user, stories=stories)

@auth.route('/account/stories')
@login_required
def my_stories():
    """User's story history"""
    page = request.args.get('page', 1, type=int)
    stories = Story.query.filter_by(user_id=current_user.id)\
                        .order_by(Story.created_at.desc())\
                        .paginate(page=page, per_page=10, error_out=False)
    
    return render_template('my_stories.html', stories=stories)



@auth.route('/account/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Account settings"""
    if request.method == 'POST':
        # Handle password change
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if current_password and new_password:
            if not current_user.check_password(current_password):
                flash('Current password is incorrect', 'error')
            elif new_password != confirm_password:
                flash('New passwords do not match', 'error')
            elif len(new_password) < 6:
                flash('New password must be at least 6 characters', 'error')
            else:
                current_user.set_password(new_password)
                db.session.commit()
                flash('Password updated successfully!', 'success')
        
        # Handle email change
        new_email = request.form.get('email')
        if new_email and new_email != current_user.email:
            if User.query.filter_by(email=new_email).first():
                flash('Email already registered', 'error')
            else:
                current_user.email = new_email
                db.session.commit()
                flash('Email updated successfully!', 'success')
    
    return render_template('settings.html', user=current_user)

# Payment routes
@auth.route('/upgrade')
@login_required
def upgrade():
    """Show upgrade plans"""
    payment_processor = PaymentProcessor()
    plans = payment_processor.get_plans()
    return render_template('upgrade.html', plans=plans, user=current_user)

@auth.route('/subscribe/<plan_type>')
@login_required
def subscribe(plan_type):
    """Start subscription process"""
    payment_processor = PaymentProcessor()
    checkout_session_id = payment_processor.create_checkout_session(current_user, plan_type)
    
    if checkout_session_id:
        return redirect(f"https://checkout.stripe.com/pay/{checkout_session_id}")
    else:
        flash('Error creating checkout session. Please try again.', 'error')
        return redirect(url_for('auth.upgrade'))

@auth.route('/payment/success')
@login_required
def payment_success():
    """Handle successful payment"""
    session_id = request.args.get('session_id')
    flash('Payment successful! Your subscription is now active.', 'success')
    return redirect(url_for('auth.account'))

@auth.route('/payment/cancel')
@login_required
def payment_cancel():
    """Handle cancelled payment"""
    flash('Payment was cancelled. You can try again anytime.', 'info')
    return redirect(url_for('auth.upgrade'))

@auth.route('/billing')
@login_required
def billing():
    """Manage billing and subscription"""
    payment_processor = PaymentProcessor()
    portal_url = payment_processor.create_portal_session(current_user)
    
    if portal_url:
        return redirect(portal_url)
    else:
        flash('Unable to access billing portal. Please contact support.', 'error')
        return redirect(url_for('auth.account'))

@auth.route('/cancel-subscription')
@login_required
def cancel_subscription():
    """Cancel user subscription"""
    payment_processor = PaymentProcessor()
    if payment_processor.cancel_subscription(current_user):
        flash('Your subscription will be cancelled at the end of the current billing period.', 'info')
    else:
        flash('Unable to cancel subscription. Please contact support.', 'error')
    
    return redirect(url_for('auth.account')) 