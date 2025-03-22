import uuid
import hashlib
import re
from datetime import datetime, timedelta

class User:
    """
    User model - represents a user in the system.
    """
    def __init__(self, user_id=None, username=None, email=None, password=None, user_type='local'):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.password = password
        self.user_type = user_type
        self.verified = False
        self.mobile_verified = False
        self.phone_number = None
        self.password_hash = None
        self.password_salt = None
        
    @staticmethod
    def hash_password(password, salt=None):
        """Hash a password with a salt"""
        if salt is None:
            salt = uuid.uuid4().hex
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return password_hash, salt
    
    @staticmethod
    def validate_password(password):
        """Validate password meets complexity requirements"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not re.search(r'[A-Za-z]', password) or not re.search(r'[0-9]', password):
            return False, "Password must contain both letters and numbers"
            
        return True, ""
    
    @staticmethod    
    def validate_email(email):
        """Validate email format"""
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return False, "Invalid email format"
        return True, ""
    
    @staticmethod
    def validate_phone(phone):
        """Validate phone number format"""
        if not phone.startswith('+') or not phone[1:].isdigit():
            return False, "Phone number format - (e.g., +1234567890)"
        return True, ""

class Verification:
    """
    Verification model - for email and mobile verification
    """
    def __init__(self, user_id=None, otp=None, type="email"):
        self.user_id = user_id
        self.otp = otp
        self.type = type  # email or mobile
        self.created_at = datetime.now()
        self.expires_at = self.created_at + timedelta(minutes=15)

class ResetToken:
    """
    Password reset token model
    """
    def __init__(self, user_id=None, otp=None):
        self.user_id = user_id
        self.otp = otp
        self.created_at = datetime.now()
        self.expires_at = self.created_at + timedelta(hours=1)

class NotificationPreference:
    """
    User notification preferences model
    """
    def __init__(self, user_id=None, notify_on_blog=True, notify_on_comment=True):
        self.user_id = user_id
        self.notify_on_blog = notify_on_blog
        self.notify_on_comment = notify_on_comment