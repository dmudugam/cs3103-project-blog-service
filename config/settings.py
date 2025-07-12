#!/usr/bin/env python
import os

# Use environment variables for Render deployment
# Default to development values if not in production
APP_HOST = os.environ.get('HOST', '0.0.0.0')  # Use 0.0.0.0 to listen on all interfaces
APP_PORT = int(os.environ.get('PORT', 10000))  # Render sets PORT environment variable
APP_DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# PostgreSQL database settings for Render
DB_HOST = 'sql5.freesqldatabase.com'
DB_USER = 'sql5789654'
DB_PASSWD = 'tTM3uj6lDi'
DB_DATABASE = 'sql5789654'
DB_PORT = 3306

SECRET_KEY = '<<ADD_SECRET_KEY>>'

LDAP_HOST = '<<ADD_LDAP_HOST>>'

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "cs3103blogservice@gmail.com"
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')
EMAIL_FROM = "cs3103blogservice@gmail.com"

# Twilio configuration for SMS
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')

# Google Gemini AI configuration
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"