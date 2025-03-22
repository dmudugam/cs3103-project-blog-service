import re
import random
import string
import uuid
import sys

# For HTML sanitization - handle missing bleach package 
try:
    import bleach
    import html
    HTML_SANITIZATION = 'bleach'
except ImportError:
    HTML_SANITIZATION = 'simple'
    print("Warning: Bleach package not installed. Using simple HTML sanitization.", file=sys.stderr)

# Allowed HTML tags and attributes for sanitization (when using bleach)
ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
                'blockquote', 'pre', 'code', 'ul', 'ol', 'li', 'a', 'img']
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title'],
    'img': ['src', 'alt']
}

def sanitize_html(text):
    """Sanitize HTML content to prevent XSS attacks but preserve emojis"""
    if text is None:
        return None
    
    if HTML_SANITIZATION == 'bleach':
        # Use bleach to strip unsafe tags while keeping safe ones
        return bleach.clean(text, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)
    else:
        # Simple sanitization regex-based approach
        dangerous_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'onerror=',
            r'onclick=',
            r'onload='
        ]
        
        result = text
        for pattern in dangerous_patterns:
            result = re.sub(pattern, '', result, flags=re.IGNORECASE | re.DOTALL)
        
        return result

def sanitize_string(text):
    """Sanitize a plain string to prevent SQL injection and XSS"""
    if text is None:
        return None
        
    if HTML_SANITIZATION == 'bleach':
        # First escape HTML entities, then escape SQL special chars
        return html.escape(text)
    else:
        # Simple string sanitization
        if isinstance(text, str):
            # Remove any script tags and common XSS vectors
            text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
            text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
            text = re.sub(r'on\w+\s*=', '', text, flags=re.IGNORECASE)
            
            # Basic SQL injection protection
            dangerous_sql = [';', '--', '/*', '*/', 'UNION', 'SELECT', 'INSERT', 'UPDATE',
                            'DELETE', 'DROP', 'TRUNCATE', 'ALTER']
            for sql in dangerous_sql:
                text = text.replace(sql, '')
        return text

def generate_otp():
    """Generate a 6-digit OTP for verification"""
    return ''.join(random.choices(string.digits, k=6))

def generate_uuid():
    """Generate a new UUID"""
    return str(uuid.uuid4())

def safe_get(dictionary, key, default=None):
    """Safely get a value from a dictionary, returning default if key doesn't exist"""
    return dictionary.get(key, default)