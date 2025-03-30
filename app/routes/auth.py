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
            user = sql_call_fetch_one('createLocalUser', (username, email, password_hash, salt))
            
            if not user:
                return make_response(jsonify({'status': 'error', 'message': 'Failed to create user'}), 500)
            
            otp = generate_otp()
            
            # Store OTP in verification table
            sql_call_fetch_one('createVerification', (user['userId'], otp))
            
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
            
            # Check if user is verified via EMAIL
            verified_result = sql_call_fetch_one('isUserVerified', (user['userId'],))
            is_verified = verified_result and verified_result.get('verified', 0) > 0
            
            try:
                # Check if user is verified via mOBILE
                mobile_verified_result = sql_call_fetch_one('isMobileVerified', (user['userId'],))
                is_mobile_verified = mobile_verified_result and mobile_verified_result.get('verified', 0) > 0
            except Exception:
                is_mobile_verified = False
            
            has_phone = safe_get(user, 'phone_number') is not None and safe_get(user, 'phone_number', '') != ''
            
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
                
                verified_result = sql_call_fetch_one('isUserVerified', (user['userId'],))
                is_verified = verified_result and verified_result.get('verified', 0) > 0

                try:
                    mobile_verified_result = sql_call_fetch_one('isMobileVerified', (user['userId'],))
                    is_mobile_verified = mobile_verified_result and mobile_verified_result.get('verified', 0) > 0
                except Exception:
                    is_mobile_verified = False
                
                has_phone = safe_get(user, 'phone_number') is not None and safe_get(user, 'phone_number', '') != ''
                
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
                verified_result = sql_call_fetch_one('isUserVerified', (user['userId'],))
                is_verified = verified_result and verified_result.get('verified', 0) > 0

                try:
                    mobile_verified_result = sql_call_fetch_one('isMobileVerified', (user['userId'],))
                    is_mobile_verified = mobile_verified_result and mobile_verified_result.get('verified', 0) > 0
                except Exception:
                    is_mobile_verified = False
                
                has_phone = safe_get(user, 'phone_number') is not None and safe_get(user, 'phone_number', '') != ''
                
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
        
        parser = reqparse.RequestParser()
        parser.add_argument('userId', type=int, required=True, help='User ID is required')
        parser.add_argument('otp', type=str, required=True, help='OTP is required')
        args = parser.parse_args()
        
        result = sql_call_fetch_one('verifyOTP', (args['userId'], args['otp']))
        
        if result and result['success']:
            return make_response(jsonify({'status': 'success', 'message': 'Email verified successfully'}), 200)
        else:
            return make_response(jsonify({'status': 'error', 'message': 'Invalid or expired OTP'}), 400)

# Request email OTP
class RequestOTP(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('userId', type=int, required=False, help='User ID is required')
        parser.add_argument('updatingEmail', type=bool, required=False, default=False)
        args = parser.parse_args()
        
        user = None
        
        if 'username' in session:
            username = session['username']
            user = sql_call_fetch_one('getUserByUsername', (username,))
        
        # If not found in session or no session, try using the userId parameter
        if not user and args.get('userId'):
            user = sql_call_fetch_one('getUserById', (args['userId'],))
        
        if not user:
            return make_response(jsonify({'status': 'error', 'message': 'User not found'}), 404)
        
        if not user.get('email'):
            return make_response(jsonify({'status': 'error', 'message': 'Please add an email address first'}), 400)
        
        # Only check verification status if were not updating email
        if not args['updatingEmail']:
            verified_result = sql_call_fetch_one('isUserVerified', (user['userId'],))
            is_verified = verified_result and verified_result.get('verified', 0) > 0
            
            if is_verified:
                return make_response(jsonify({'status': 'error', 'message': 'Email is already verified'}), 400)
        
        # Check if there's a pending email update for this user
        pending_email = None
        try:
            pending_result = sql_call_fetch_one('getPendingEmail', (user['userId'],))
            if pending_result and 'newEmail' in pending_result:
                pending_email = pending_result['newEmail']
                print(f"Found pending email: {pending_email}")
            else:
                print(f"No pending email found or unexpected structure: {pending_result}")
        except Exception as e:
            print(f"Error checking pending email: {e}")

        email_to_use = pending_email if pending_email else user.get('email')
        print(f"Using email for OTP: {email_to_use}")
        
        otp = generate_otp()
        
        # Update verification record
        sql_call_fetch_one('createVerification', (user['userId'], otp))
        
        send_verification_email(email_to_use, user['username'], otp)
        
        return make_response(jsonify({
            'status': 'success', 
            'message': 'Verification OTP sent to email',
            'userId': user['userId']
        }), 200)

# Mobile OTP verification
class VerifyMobileOTP(Resource):
    def post(self):
        if not request.is_json:
            return make_response(jsonify({'status': 'error', 'message': 'Request must be JSON'}), 400)
        parser = reqparse.RequestParser()
        parser.add_argument('userId', type=int, required=True, help='User ID is required')
        parser.add_argument('otp', type=str, required=True, help='OTP is required')
        args = parser.parse_args()

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
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('userId', type=int, required=False, help='User ID is required')
        parser.add_argument('updatingPhone', type=bool, required=False, default=False)
        parser.add_argument('phone', type=str, required=False, help='Phone number')
        args = parser.parse_args()
        
        user = None
        
        # Try to get user from the session if logged in
        if 'username' in session:
            username = session['username']
            user = sql_call_fetch_one('getUserByUsername', (username,))
        
        if not user and args.get('userId'):
            user = sql_call_fetch_one('getUserById', (args['userId'],))
        
        if not user:
            return make_response(jsonify({'status': 'error', 'message': 'User not found'}), 404)
        
        # If phone is provided in the request, use that and update the user's record
        phone_to_use = None
        if args.get('phone'):
            phone_to_use = args['phone']
            
            try:
                sql_call_fetch_one('updateUserPhone', (user['userId'], phone_to_use))
                print(f"Updated phone for user {user['userId']} to {phone_to_use}")
            except Exception as e:
                print(f"Error updating phone: {e}")
        if not phone_to_use:
            # First check if there's a pending phone number update for this user
            pending_phone = None
            try:
                pending_result = sql_call_fetch_one('getPendingPhone', (user['userId'],))
                if pending_result and 'newPhone' in pending_result:
                    pending_phone = pending_result['newPhone']
                    print(f"Found pending phone: {pending_phone}")
            except Exception as e:
                print(f"Error checking pending phone: {e}")
            
            if pending_phone:
                phone_to_use = pending_phone
            elif safe_get(user, 'phone_number'):
                phone_to_use = user.get('phone_number')
        
        if not phone_to_use:
            return make_response(jsonify({'status': 'error', 'message': 'No phone number found. Please add a phone number first.'}), 400)
        
        if not args['updatingPhone']:
            try:
                # Check if user is already verified
                mobile_verified_result = sql_call_fetch_one('isMobileVerified', (user['userId'],))
                is_mobile_verified = mobile_verified_result and mobile_verified_result.get('verified', 0) > 0
                
                if is_mobile_verified and not pending_phone:
                    return make_response(jsonify({'status': 'error', 'message': 'Phone is already verified'}), 400)
            except Exception as e:
                print(f"Error checking mobile verification: {e}")
                pass
        
        if not is_sms_enabled():
            return make_response(jsonify({'status': 'error', 'message': 'SMS functionality is not enabled on the server'}), 400)
        
        otp = generate_otp()
        
        try:
            # Update verification record
            sql_call_fetch_one('createMobileVerification', (user['userId'], otp))
        except Exception as e:
            print(f"Error creating mobile verification: {e}")
            return make_response(jsonify({'status': 'error', 'message': f'Mobile verification database error: {str(e)}'}), 400)
        
        print(f"Sending OTP to phone: {phone_to_use}")
        sms_sent = send_verification_sms(phone_to_use, user['username'], otp)
        
        if sms_sent:
            return make_response(jsonify({
                'status': 'success', 
                'message': 'Verification OTP sent to phone',
                'userId': user['userId'],
                'phoneUsed': phone_to_use
            }), 200)
        else:
            return make_response(jsonify({'status': 'error', 'message': 'Failed to send SMS. Please try again or contact support.'}), 500)

class RequestPasswordReset(Resource):
    def post(self):
        if not request.is_json:
            return make_response(jsonify({'status': 'error', 'message': 'Request must be JSON'}), 400)
        
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
        if user and user['user_type'] == 'local': 
            try:
                otp = generate_otp()
                
                sql_call_fetch_one('createPasswordResetOTP', (user['userId'], otp))
            
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
        
        # Verify OTP first to make sure its valid and get the user
        user = sql_call_fetch_one('verifyResetOTP', (otp,))
        
        if not user:
            return make_response(jsonify({
                'status': 'error', 
                'message': 'Invalid or expired reset OTP'
            }), 400)
        
        # For local users, check if the new password is the same as the current one
        existing_user = sql_call_fetch_one('validateLocalUser', (user['username'],))
        if existing_user and 'password_salt' in existing_user:
            # Calculate hash for the new password with the existing salt
            new_password_hash = hashlib.sha256((args['password'] + existing_user['password_salt']).encode()).hexdigest()
            
            # Compare with the existing hash
            if new_password_hash == existing_user['password_hash']:
                return make_response(jsonify({
                    'status': 'error',
                    'message': 'New password must be different from your last five passwords.'
                }), 400)
        
        # Generate salt and hash the password
        salt = uuid.uuid4().hex
        password_hash = hashlib.sha256((args['password'] + salt).encode()).hexdigest()
        
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
        
        parser = reqparse.RequestParser()
        parser.add_argument('otp', type=str, required=True, help='Reset OTP is required')
        args = parser.parse_args()

        otp = sanitize_string(args['otp'])
        
        if not otp:
            return make_response(jsonify({'status': 'error', 'message': 'Reset OTP is required'}), 400)
        
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

