from flask import current_app
import sys

# For SMS OTP
try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    print("Warning: Twilio package not installed. SMS functionality will be disabled.", file=sys.stderr)

def get_twilio_client():
    # Get the client if available
    if not TWILIO_AVAILABLE:
        return None
    
    try:
        client = Client(
            current_app.config['TWILIO_ACCOUNT_SID'], 
            current_app.config['TWILIO_AUTH_TOKEN']
        )
        return client
    except Exception as e:
        print(f"Twilio client initialization failed: {e}", file=sys.stderr)
        return None

def send_verification_sms(phone_number, username, otp):
    if not phone_number:
        print("Cannot send verification SMS: No phone number provided", file=sys.stderr)
        return False
    
    client = get_twilio_client()
    if not client:
        print("SMS functionality is disabled. Cannot send verification SMS.", file=sys.stderr)
        return False
    
    try:
        message = client.messages.create(
            body=f"Hello {username}, your Blog Service verification code is: {otp}. This code will expire in 15 minutes.",
            from_=current_app.config['TWILIO_PHONE_NUMBER'],
            to=phone_number
        )
        print(f"Verification SMS sent to {phone_number}: {message.sid}")
        return True
    except Exception as e:
        print(f"Failed to send SMS: {e}", file=sys.stderr)
        return False

def is_sms_enabled():
    return TWILIO_AVAILABLE and get_twilio_client() is not None