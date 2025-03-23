from flask import request, session, make_response, jsonify
from flask_restful import Resource, reqparse
from ldap3 import Server, Connection, ALL
from ldap3.core.exceptions import LDAPException
import hashlib
import uuid
import re

from app.services.db_service import sql_call_fetch_one, sql_call_fetch_all
from app.services.email_service import send_verification_email, send_password_reset_otp
from app.services.sms_service import send_verification_sms, is_sms_enabled
from app.utils.helpers import sanitize_string, generate_otp, safe_get
from app.utils.decorators import login_required

class UserRegistration(Resource):
    def post(self):
        if not request.is_json:
            return make_response(jsonify({'status': 'error', 'message': 'Request must be JSON'}), 400)
        
        # Parse request
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True, help='Username is required')
        parser.add_argument('email', type=str, required=True, help='Email is required')
        parser.add_argument('password', type=str, required=True, help='Password is required')
        args = parser.parse_args()
        
        # Sanitize inputs
        username = sanitize_string(args['username'])
        email = sanitize_string(args['email'])
        
        if not username or not email or not args['password']:
            return make_response(jsonify({'status': 'error', 'message': 'All fields are required after sanitization'}), 400)
        
        # Validate email format
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return make_response(jsonify({'status': 'error', 'message': 'Invalid email format'}), 400)
        
        # Validate password strength
        if len(args['password']) < 8 or not re.search(r'[A-Za-z]', args['password']) or not re.search(r'[0-9]', args['password']):
            return make_response(jsonify({'status': 'error', 'message': 'Password must be at least 8 characters and contain both letters and numbers'}), 400)
        
        # Check if username already exists
        existing_user = sql_call_fetch_one('getUserByUsername', (username,))
        if existing_user:
            return make_response(jsonify({'status': 'error', 'message': 'Username already exists'}), 400)
        
        # Check if email already exists
        existing_email_user = sql_call_fetch_one('getUserByEmail', (email,))
        if existing_email_user:
            return make_response(jsonify({'status': 'error', 'message': 'Email address already in use'}), 400)
        
        # Generate salt and hash the password
        salt = uuid.uuid4().hex
        password_hash = hashlib.sha256((args['password'] + salt).encode()).hexdigest()
        
        try:
            # Create user
            user = sql_call_fetch_one('createLocalUser', (username, email, password_hash, salt))
            
            if not user:
                return make_response(jsonify({'status': 'error', 'message': 'Failed to create user'}), 500)
            
            # Generate OTP for verification
            otp = generate_otp()
            
            # Store OTP in verification table
            sql_call_fetch_one('createVerification', (user['userId'], otp))
            
            # Send verification email with OTP
            send_verification_email(email, username, otp)
            
            # Return success response
            return make_response(jsonify({
                'status': 'success',
                'message': 'User registered successfully. Check your email for verification OTP.',
                'userId': user['userId'],
                'username': user['username'],
                'email': user['email']
            }), 201)
            
        except Exception as e:
            return make_response(jsonify({'status': 'error', 'message': f'Registration error: {str(e)}'}), 500)

class AuthLogin(Resource):
    def post(self):
        if not request.is_json:
            return make_response(jsonify({'status': 'error', 'message': 'Request must be JSON'}), 400)
        
        # Parse request
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str, required=True, help='Username is required')
        parser.add_argument('password', type=str, required=True, help='Password is required')
        parser.add_argument('type', type=str, required=False, default='ldap', help='Login type (ldap or local)')
        args = parser.parse_args()
        
        # Sanitize username and login type
        username = sanitize_string(args['username'])
        login_type = sanitize_string(args['type'])
        
        if not username:
            return make_response(jsonify({'status': 'error', 'message': 'Username is required after sanitization'}), 400)
        
        if login_type == 'local':
            # Local user authentication
            user = sql_call_fetch_one('validateLocalUser', (username,))
            
            if not user or 'password_hash' not in user or 'password_salt' not in user:
                return make_response(jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401)
            
            # Verify password
            password_hash = hashlib.sha256((args['password'] + user['password_salt']).encode()).hexdigest()
            if password_hash != user['password_hash']:
                return make_response(jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401)
            
            # Authentication successful
            session.permanent = True
            session['username'] = username
            session['user_type'] = 'local'
            
            # Check if user is verified via email
            verified_result = sql_call_fetch_one('isUserVerified', (user['userId'],))
            is_verified = verified_result and verified_result.get('verified', 0) > 0
            
            # Mobile verification
            try:
                # Check if user is verified via mobile
                mobile_verified_result = sql_call_fetch_one('isMobileVerified', (user['userId'],))
                is_mobile_verified = mobile_verified_result and mobile_verified_result.get('verified', 0) > 0
            except Exception:
                is_mobile_verified = False
            
            # Access for phone number
            has_phone = safe_get(user, 'phone_number') is not None and safe_get(user, 'phone_number', '') != ''
            
            # Check if user has email
            has_email = user.get('email') is not None and user.get('email', '') != ''
            
            sms_enabled = is_sms_enabled()
            
            response = {
                'status': 'success',
                'message': 'Login successful',
                'token': 'session_based',
                'userId': user['userId'],
                'username': user['username'],
                'email': user.get('email'),
                'phoneNumber': safe_get(user, 'phone_number'),
                'verified': is_verified,
                'mobileVerified': is_mobile_verified,
                'hasEmail': has_email,
                'hasPhone': has_phone,
                'smsEnabled': sms_enabled,
                'userType': 'local'
            }
            
            return make_response(jsonify(response), 200)
        else:
            # LDAP authentication
            try:
                from flask import current_app
                ldap_server = Server(host=current_app.config['LDAP_HOST'])
                ldap_connection = Connection(
                    ldap_server,
                    raise_exceptions=True,
                    user='uid=' + username + ', ou=People,ou=fcs,o=unb',
                    password=args['password']
                )
                ldap_connection.open()
                ldap_connection.start_tls()
                ldap_connection.bind()
                
                # Authentication successful
                user = sql_call_fetch_one('createLdapUser', (username,))
                
                if not user:
                    return make_response(jsonify({'status': 'error', 'message': 'Failed to create user record'}), 500)
                
                # Set session
                session.permanent = True
                session['username'] = username
                session['user_type'] = 'ldap'
                
                # Check if user is verified via email
                verified_result = sql_call_fetch_one('isUserVerified', (user['userId'],))
                is_verified = verified_result and verified_result.get('verified', 0) > 0
                
                # Access for mobile verification
                try:
                    # Check if user is verified via mobile
                    mobile_verified_result = sql_call_fetch_one('isMobileVerified', (user['userId'],))
                    is_mobile_verified = mobile_verified_result and mobile_verified_result.get('verified', 0) > 0
                except Exception:
                    is_mobile_verified = False
                
                # Access for phone number
                has_phone = safe_get(user, 'phone_number') is not None and safe_get(user, 'phone_number', '') != ''
                
                # Check if user has email
                has_email = user.get('email') is not None and user.get('email', '') != ''
                
                sms_enabled = is_sms_enabled()
                
                response = {
                    'status': 'success',
                    'message': 'Login successful',
                    'token': 'session_based',
                    'userId': user['userId'],
                    'username': user['username'],
                    'email': user.get('email'),
                    'phoneNumber': safe_get(user, 'phone_number'),
                    'verified': is_verified,
                    'mobileVerified': is_mobile_verified,
                    'hasEmail': has_email,
                    'hasPhone': has_phone,
                    'smsEnabled': sms_enabled,
                    'userType': 'ldap'
                }
                
                return make_response(jsonify(response), 200)
            
            except LDAPException as e:
                return make_response(jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401)
            finally:
                if 'ldap_connection' in locals() and ldap_connection:
                    ldap_connection.unbind()

    # GET method to support session checks
    def get(self):
        if 'username' in session:
            username = session['username']
            user = sql_call_fetch_one('getUserByUsername', (username,))
            
            if user:
                # Check if user is verified via email
                verified_result = sql_call_fetch_one('isUserVerified', (user['userId'],))
                is_verified = verified_result and verified_result.get('verified', 0) > 0
                
                # Access for mobile verification
                try:
                    # Check if user is verified via mobile
                    mobile_verified_result = sql_call_fetch_one('isMobileVerified', (user['userId'],))
                    is_mobile_verified = mobile_verified_result and mobile_verified_result.get('verified', 0) > 0
                except Exception:
                    is_mobile_verified = False
                
                # Access for phone number
                has_phone = safe_get(user, 'phone_number') is not None and safe_get(user, 'phone_number', '') != ''
                
                # Check if user has email
                has_email = user.get('email') is not None and user.get('email', '') != ''
                
                sms_enabled = is_sms_enabled()
                
                response = {
                    'status': 'success',
                    'message': 'Authenticated',
                    'userId': user['userId'],
                    'username': user['username'],
                    'email': user.get('email'),
                    'phoneNumber': safe_get(user, 'phone_number'),
                    'verified': is_verified,
                    'mobileVerified': is_mobile_verified,
                    'hasEmail': has_email,
                    'hasPhone': has_phone,
                    'smsEnabled': sms_enabled,
                    'userType': user.get('user_type', 'ldap')
                }
                return make_response(jsonify(response), 200)
        
        return make_response(jsonify({'status': 'error', 'message': 'Not authenticated'}), 401)

class AuthLogout(Resource):
    @login_required
    def post(self):
        session.pop('username', None)
        session.pop('user_type', None)
        return make_response(jsonify({'status': 'success', 'message': 'Logout successful'}), 200)

# Email OTP verification
class VerifyOTP(Resource):
    def post(self):
        if not request.is_json:
            return make_response(jsonify({'status': 'error', 'message': 'Request must be JSON'}), 400)
        
        # Parse request
        parser = reqparse.RequestParser()
        parser.add_argument('userId', type=int, required=True, help='User ID is required')
        parser.add_argument('otp', type=str, required=True, help='OTP is required')
        args = parser.parse_args()
        
        # Verify OTP
        result = sql_call_fetch_one('verifyOTP', (args['userId'], args['otp']))
        
        if result and result['success']:
            return make_response(jsonify({'status': 'success', 'message': 'Email verified successfully'}), 200)
        else:
            return make_response(jsonify({'status': 'error', 'message': 'Invalid or expired OTP'}), 400)

# Request email OTP
class RequestOTP(Resource):
    def post(self):
        # Check if request has JSON
        user_id = None
        if request.is_json:
            parser = reqparse.RequestParser()
            parser.add_argument('userId', type=int)
            args = parser.parse_args()
            user_id = args.get('userId')
        
        # If no userId provided, try to get from session username
        if user_id is None:
            if 'username' not in session:
                return make_response(jsonify({'status': 'error', 'message': 'User not logged in'}), 401)
            
            # Get user by username from session
            username = session['username']
            user = sql_call_fetch_one('getUserByUsername', (username,))
            
            if not user:
                return make_response(jsonify({'status': 'error', 'message': 'User not found'}), 404)
                
            user_id = user['userId']
        else:
            # Get user info for the provided user ID
            user = sql_call_fetch_one('getUserById', (user_id,))
            
            if not user:
                return make_response(jsonify({'status': 'error', 'message': 'User not found'}), 404)
        
        # Check if user has an email
        if not user.get('email'):
            return make_response(jsonify({'status': 'error', 'message': 'Please add an email address first'}), 400)
        
        # Check if user is already verified
        verified_result = sql_call_fetch_one('isUserVerified', (user['userId'],))
        is_verified = verified_result and verified_result.get('verified', 0) > 0
        
        if is_verified:
            return make_response(jsonify({'status': 'error', 'message': 'Email is already verified'}), 400)
        
        # Generate new OTP
        otp = generate_otp()
        
        # Update verification record
        sql_call_fetch_one('createVerification', (user['userId'], otp))
        
        # Send verification email
        send_verification_email(user['email'], user['username'], otp)
        
        return make_response(jsonify({'status': 'success', 'message': 'Verification OTP sent to email'}), 200)

# Mobile OTP verification
class VerifyMobileOTP(Resource):
    def post(self):
        if not request.is_json:
            return make_response(jsonify({'status': 'error', 'message': 'Request must be JSON'}), 400)
        
        # Parse request
        parser = reqparse.RequestParser()
        parser.add_argument('userId', type=int, required=True, help='User ID is required')
        parser.add_argument('otp', type=str, required=True, help='OTP is required')
        args = parser.parse_args()
        
        # Verify OTP
        try:
            result = sql_call_fetch_one('verifyMobileOTP', (args['userId'], args['otp']))
            
            if result and result.get('success'):
                return make_response(jsonify({'status': 'success', 'message': 'Phone number verified successfully'}), 200)
            else:
                return make_response(jsonify({'status': 'error', 'message': 'Invalid or expired OTP'}), 400)
        except Exception as e:
            return make_response(jsonify({'status': 'error', 'message': 'Mobile verification not available. Database needs to be updated.'}), 400)

# Request mobile OTP
class RequestMobileOTP(Resource):
    @login_required
    def post(self):
        # Get user from session
        username = session['username']
        user = sql_call_fetch_one('getUserByUsername', (username,))
        
        if not user:
            return make_response(jsonify({'status': 'error', 'message': 'User not found'}), 404)
        
        # Check if user has a phone number
        if not safe_get(user, 'phone_number'):
            return make_response(jsonify({'status': 'error', 'message': 'Please add a phone number first'}), 400)
        
        # Check if mobile verification tables exist
        try:
            # Check if user is already verified
            mobile_verified_result = sql_call_fetch_one('isMobileVerified', (user['userId'],))
            is_mobile_verified = mobile_verified_result and mobile_verified_result.get('verified', 0) > 0
            
            if is_mobile_verified:
                return make_response(jsonify({'status': 'error', 'message': 'Phone is already verified'}), 400)
        except Exception as e:
            return make_response(jsonify({'status': 'error', 'message': 'Mobile verification not available. Database needs to be updated.'}), 400)
        
        # Make sure SMS is enabled
        if not is_sms_enabled():
            return make_response(jsonify({'status': 'error', 'message': 'SMS functionality is not enabled on the server'}), 400)
        
        # Generate new OTP
        otp = generate_otp()
        
        try:
            # Update verification record
            sql_call_fetch_one('createMobileVerification', (user['userId'], otp))
        except Exception as e:
            return make_response(jsonify({'status': 'error', 'message': 'Mobile verification not available. Database needs to be updated.'}), 400)
        
        # Send verification SMS
        sms_sent = send_verification_sms(user['phone_number'], user['username'], otp)
        
        if sms_sent:
            return make_response(jsonify({'status': 'success', 'message': 'Verification OTP sent to phone'}), 200)
        else:
            return make_response(jsonify({'status': 'error', 'message': 'Failed to send SMS. Please try again or contact support.'}), 500)

class RequestPasswordReset(Resource):
    def post(self):
        if not request.is_json:
            return make_response(jsonify({'status': 'error', 'message': 'Request must be JSON'}), 400)
        
        # Parse request
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True, help='Email is required')
        args = parser.parse_args()
        
        # Sanitize inputs
        email = sanitize_string(args['email'])
        
        if not email:
            return make_response(jsonify({'status': 'error', 'message': 'Email is required'}), 400)
        
        # Validate email format
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return make_response(jsonify({'status': 'error', 'message': 'Invalid email format'}), 400)
        
        # Find user by email
        user = sql_call_fetch_one('getUserByEmail', (email,))
        
        # Always return success
        if user and user['user_type'] == 'local':  # Only allow resets for local accounts, not LDAP
            try:
                # Generate a 6-digit OTP
                otp = generate_otp()
                
                # Store OTP in database
                sql_call_fetch_one('createPasswordResetOTP', (user['userId'], otp))
                
                # Send reset email with OTP
                send_password_reset_otp(email, user['username'], otp)
            except Exception as e:
                print(f"Password reset process error: {e}")
        
        return make_response(jsonify({
            'status': 'success',
            'message': 'If an account with that email exists, a password reset OTP has been sent.'
        }), 200)

class CompletePasswordReset(Resource):
    def post(self):
        if not request.is_json:
            return make_response(jsonify({'status': 'error', 'message': 'Request must be JSON'}), 400)
        
        # Parse request
        parser = reqparse.RequestParser()
        parser.add_argument('otp', type=str, required=True, help='Reset OTP is required')
        parser.add_argument('password', type=str, required=True, help='New password is required')
        args = parser.parse_args()
        
        # Sanitize inputs
        otp = sanitize_string(args['otp'])
        
        if not otp or not args['password']:
            return make_response(jsonify({'status': 'error', 'message': 'Reset OTP and new password are required'}), 400)
        
        # Validate password strength
        if len(args['password']) < 8 or not re.search(r'[A-Za-z]', args['password']) or not re.search(r'[0-9]', args['password']):
            return make_response(jsonify({'status': 'error', 'message': 'Password must be at least 8 characters and contain both letters and numbers'}), 400)
        
        # Verify OTP first to make sure its valid
        user = sql_call_fetch_one('verifyResetOTP', (otp,))
        
        if not user:
            return make_response(jsonify({
                'status': 'error', 
                'message': 'Invalid or expired reset OTP'
            }), 400)
        
        # Generate salt and hash the password
        salt = uuid.uuid4().hex
        password_hash = hashlib.sha256((args['password'] + salt).encode()).hexdigest()
        
        # Update the password and remove the reset OTP
        result = sql_call_fetch_one('resetPasswordWithOTP', (otp, password_hash, salt))
        
        if not result or not result.get('success'):
            return make_response(jsonify({
                'status': 'error', 
                'message': 'Failed to reset password'
            }), 500)
        
        # Return success
        return make_response(jsonify({
            'status': 'success',
            'message': 'Password has been reset successfully. You can now log in with your new password.'
        }), 200)

class VerifyResetOTP(Resource):
    def post(self):
        if not request.is_json:
            return make_response(jsonify({'status': 'error', 'message': 'Request must be JSON'}), 400)
        
        # Parse request
        parser = reqparse.RequestParser()
        parser.add_argument('otp', type=str, required=True, help='Reset OTP is required')
        args = parser.parse_args()
        
        # Sanitize inputs
        otp = sanitize_string(args['otp'])
        
        if not otp:
            return make_response(jsonify({'status': 'error', 'message': 'Reset OTP is required'}), 400)
        
        # Verify OTP
        user = sql_call_fetch_one('verifyResetOTP', (otp,))
        
        if not user:
            return make_response(jsonify({
                'status': 'error', 
                'message': 'Invalid or expired reset OTP'
            }), 400)
        
        # Return success with username
        return make_response(jsonify({
            'status': 'success',
            'message': 'Valid reset OTP',
            'username': user['username'],
            'userId': user['userId']
        }), 200)