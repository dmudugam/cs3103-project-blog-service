from flask import request, session, make_response, jsonify
from flask_restful import Resource, reqparse
import re

from app.services.db_service import sql_call_fetch_one, sql_call_fetch_all
from app.utils.helpers import sanitize_string
from app.utils.decorators import login_required

class UserList(Resource):
    def get(self):
        # Parse query parameters
        parser = reqparse.RequestParser()
        parser.add_argument('limit', type=int, required=False, default=20, help='Maximum number of users to return')
        parser.add_argument('offset', type=int, required=False, default=0, help='Number of users to skip for pagination')
        args = parser.parse_args()
        
        # Get users from database
        users = sql_call_fetch_all('getUsers', (args['limit'], args['offset']))
        
        response = make_response(jsonify(users), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

class UserDetail(Resource):
    def get(self, userId):
        user = sql_call_fetch_one('getUserById', (userId,))
        if not user:
            return make_response(jsonify({'status': 'error', 'message': 'User not found'}), 404)
        
        response = make_response(jsonify(user), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

class UserEmail(Resource):
    @login_required
    def put(self):
        if not request.is_json:
            return make_response(jsonify({'status': 'error', 'message': 'Request must be JSON'}), 400)
        
        # Parse request
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True, help='Email is required')
        args = parser.parse_args()
        
        # Sanitize inputs
        email = sanitize_string(args['email'])
        
        if not email:
            return make_response(jsonify({'status': 'error', 'message': 'Email is required after sanitization'}), 400)
        
        # Validate email format
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return make_response(jsonify({'status': 'error', 'message': 'Invalid email format'}), 400)
        
        # Get the current user
        username = session['username']
        
        # Check if email already exists for a different user
        existing_email_user = sql_call_fetch_one('getUserByEmail', (email,))
        if existing_email_user and existing_email_user['username'] != username:
            return make_response(jsonify({'status': 'error', 'message': 'Email address is already in use by another account'}), 400)
        
        # Get user from session
        user = sql_call_fetch_one('getUserByUsername', (username,))
        
        if not user:
            return make_response(jsonify({'status': 'error', 'message': 'User not found'}), 404)
        
        # Update users email
        updated_user = sql_call_fetch_one('updateUserEmail', (user['userId'], email))
        
        if not updated_user:
            return make_response(jsonify({'status': 'error', 'message': 'Failed to update email'}), 500)
        
        # Generate OTP for verification
        from app.utils.helpers import generate_otp
        otp = generate_otp()
        
        # Store OTP in verification table
        sql_call_fetch_one('createVerification', (updated_user['userId'], otp))
        
        # Send verification email with OTP
        from app.services.email_service import send_verification_email
        send_verification_email(email, updated_user['username'], otp)
        
        return make_response(jsonify(updated_user), 200)

class UserPhone(Resource):
    @login_required
    def put(self):
        if not request.json:
            return make_response(jsonify({'status': 'error', 'message': 'No JSON data provided'}), 400)
        
        # Parse request
        parser = reqparse.RequestParser()
        parser.add_argument('phone', type=str, required=True, help='Phone number is required')
        args = parser.parse_args()
        
        # Sanitize phone
        phone = sanitize_string(args['phone'])
        
        if not phone:
            return make_response(jsonify({'status': 'error', 'message': 'Phone number is required after sanitization'}), 400)
        
        # Validate phone number format
        if not phone.startswith('+') or not phone[1:].isdigit():
            return make_response(jsonify({'status': 'error', 'message': 'Phone number must be in E.164 format (e.g., +1234567890)'}), 400)
        
        # Get user from session
        username = session['username']
        user = sql_call_fetch_one('getUserByUsername', (username,))
        
        if not user:
            return make_response(jsonify({'status': 'error', 'message': 'User not found'}), 404)
        
        # Check if user has phone_number, temporarily disable SMS functionality if not
        if 'phone_number' not in user:
            return make_response(jsonify({
                'status': 'error',
                'message': 'Phone number functionality is not available. The database needs to be updated.'
            }), 400)
        
        # Update user's phone number
        updated_user = sql_call_fetch_one('updateUserPhone', (user['userId'], phone))
        
        if not updated_user:
            return make_response(jsonify({'status': 'error', 'message': 'Failed to update phone number'}), 500)
        
        # Generate OTP for verification
        from app.utils.helpers import generate_otp
        otp = generate_otp()
        
        # Store OTP in verification table
        sql_call_fetch_one('createMobileVerification', (updated_user['userId'], otp))
        
        # Check if SMS is enabled and try to send it
        from app.services.sms_service import send_verification_sms, is_sms_enabled
        sms_sent = False
        if is_sms_enabled():
            sms_sent = send_verification_sms(phone, updated_user['username'], otp)
        
        # Include SMS status in response
        response_data = {**updated_user, 'sms_sent': sms_sent}
        
        return make_response(jsonify(response_data), 200)
    
class UserBlogList(Resource):
    def get(self, userId):
        # Check if user exists
        user = sql_call_fetch_one('getUserById', (userId,))
        if not user:
            return make_response(jsonify({'status': 'error', 'message': 'User not found'}), 404)
        
        # Use direct request.args instead of reqparse
        newer_than = request.args.get('newerThan')
        limit = request.args.get('limit', default=20, type=int)
        offset = request.args.get('offset', default=0, type=int)
        
        # Convert date string to date object if provided
        if newer_than:
            try:
                from datetime import datetime
                newer_than = datetime.strptime(newer_than, '%Y-%m-%d').date()
            except ValueError:
                return make_response(jsonify({'status': 'error', 'message': 'Invalid date format. Use YYYY-MM-DD'}), 400)
        
        # Get blogs from database
        blogs = sql_call_fetch_all('getBlogsByUserId', (userId, newer_than, limit, offset))
        
        response = make_response(jsonify(blogs), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    
class UserNotificationPreferences(Resource):
    @login_required
    def get(self):
        # Get user from session
        username = session['username']
        user = sql_call_fetch_one('getUserByUsername', (username,))
        
        if not user:
            return make_response(jsonify({'status': 'error', 'message': 'User not found'}), 404)
        
        # Get notification preferences
        prefs = sql_call_fetch_one('getUserNotificationPreferences', (user['userId'],))
        
        response = make_response(jsonify(prefs), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    
    @login_required
    def put(self):
        if not request.json:
            return make_response(jsonify({'status': 'error', 'message': 'No JSON data provided'}), 400)
        
        # Parse request
        parser = reqparse.RequestParser()
        parser.add_argument('notifyOnBlog', type=bool, required=True, help='notifyOnBlog is required')
        parser.add_argument('notifyOnComment', type=bool, required=True, help='notifyOnComment is required')
        args = parser.parse_args()
        
        # Get user from session
        username = session['username']
        user = sql_call_fetch_one('getUserByUsername', (username,))
        
        if not user:
            return make_response(jsonify({'status': 'error', 'message': 'User not found'}), 404)
        
        # Update notification preferences
        prefs = sql_call_fetch_one('updateNotificationPreferences', (
            user['userId'], 
            args['notifyOnBlog'],
            args['notifyOnComment']
        ))
        
        if not prefs:
            return make_response(jsonify({'status': 'error', 'message': 'Failed to update notification preferences'}), 500)
        
        return make_response(jsonify(prefs), 200)