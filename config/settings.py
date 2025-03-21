#!/usr/bin/env python
APP_HOST = 'cs3103.cs.unb.ca'
APP_PORT = 8006
APP_DEBUG = True

DB_HOST = 'localhost'
DB_USER = '<<ADD_DB_USER>>'
DB_PASSWD = '<<ADD_DB_PASSWORD>>'
DB_DATABASE = '<<ADD_DATABASE>>'

SECRET_KEY = '<<ADD_SECRET_KEY>>'

LDAP_HOST = '<<ADD_LDAP_HOST>>'

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "cs3103blogservice@gmail.com"
SMTP_PASSWORD = "<<ADD_PASSWORD>>"
EMAIL_FROM = "cs3103blogservice@gmail.com"

# Twilio configuration for SMS
TWILIO_ACCOUNT_SID = "<<ADD_ACCOUNT_SID>>"
TWILIO_AUTH_TOKEN = "<<ADD_AUTH_TOKEN>>" 
TWILIO_PHONE_NUMBER = "+19499983365"

# Google Gemini AI configuration
GEMINI_API_KEY = "<<ADD_API_KEY>>"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"