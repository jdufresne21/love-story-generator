"""
User Models - Handles user authentication and account management
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import uuid

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication and account management"""
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Subscription/plan info
    plan_type = db.Column(db.String(20), default='free')  # free, basic, premium, pro
    plan_start_date = db.Column(db.DateTime, default=datetime.utcnow)
    plan_end_date = db.Column(db.DateTime)
    
    # Usage tracking
    stories_created = db.Column(db.Integer, default=0)
    stories_this_month = db.Column(db.Integer, default=0)
    last_story_date = db.Column(db.DateTime)
    
    # Relationships
    stories = db.relationship('Story', backref='user', lazy=True)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if password is correct"""
        return check_password_hash(self.password_hash, password)
    
    def can_create_story(self):
        """Check if user can create a new story based on their plan"""
        if self.plan_type == 'free':
            return self.stories_this_month < 1
        elif self.plan_type == 'basic':
            return self.stories_this_month < 3
        elif self.plan_type == 'premium':
            return self.stories_this_month < 10
        elif self.plan_type == 'pro':
            return True  # Unlimited
        return False
    
    def get_plan_limits(self):
        """Get story limits for current plan"""
        limits = {
            'free': 1,
            'basic': 3,
            'premium': 10,
            'pro': -1  # Unlimited
        }
        return limits.get(self.plan_type, 1)
    
    def reset_monthly_usage(self):
        """Reset monthly story count if it's a new month"""
        if not self.last_story_date or self.last_story_date.month != datetime.utcnow().month:
            self.stories_this_month = 0
            self.last_story_date = datetime.utcnow()
    
    def increment_story_count(self):
        """Increment story counters"""
        self.reset_monthly_usage()
        self.stories_created += 1
        self.stories_this_month += 1
        self.last_story_date = datetime.utcnow()
        db.session.commit()

class Story(db.Model):
    """Story model to track user stories"""
    
    id = db.Column(db.Integer, primary_key=True)
    story_id = db.Column(db.String(50), unique=True, nullable=False)  # The short ID used in URLs
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200))
    story_text = db.Column(db.Text, nullable=False)
    story_data = db.Column(db.JSON)  # Store form data as JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_public = db.Column(db.Boolean, default=False)
    
    def __init__(self, **kwargs):
        super(Story, self).__init__(**kwargs)
        if not self.story_id:
            self.story_id = str(uuid.uuid4())[:8]

class UserSession(db.Model):
    """Track user sessions for analytics"""
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    session_id = db.Column(db.String(100), unique=True, nullable=False)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True) 