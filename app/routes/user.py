from flask import request, session, make_response, jsonify
from flask_restful import Resource, reqparse
import re

from app.services.db_service import sql_call_fetch_one, sql_call_fetch_all
from app.utils.helpers import sanitize_string
from app.utils.decorators import login_required

class UserList(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('limit', type=int, required=False, default=20, help='Maximum number of users to return')
        parser.add_argument('offset', type=int, required=False, default=0, help='Number of users to skip for pagination')
        args = parser.parse_args()
        
        # Get users
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
        
        parser = reqparse.RequestParser()
        parser.add_argument('email', type=str, required=True, help='Email is required')
        args = parser.parse_args()
        
        # Sanitize
        email = sanitize_string(args['email'])
        
        if not email:
            return make_response(jsonify({'status': 'error', 'message': 'Email is required after sanitization'}), 400)
        
        # Validate email
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return make_response(jsonify({'status': 'error', 'message': 'Invalid email format'}), 400)
        
        username = session['username']
        
        # Get user
        user = sql_call_fetch_one('getUserByUsername', (username,))
        
        if not user:
            return make_response(jsonify({'status': 'error', 'message': 'User not found'}), 404)
        
        # Check if the new email is the same as the current one
        if user.get('email') and user['email'] == email:
            return make_response(jsonify({'status': 'error', 'message': 'The email address is the same as your current one'}), 400)
        
        # Check if email already exists for a different user
        existing_email_user = sql_call_fetch_one('getUserByEmail', (email,))
        if existing_email_user and existing_email_user['username'] != username:
            return make_response(jsonify({'status': 'error', 'message': 'Email address is already in use by another account'}), 400)
        
        updated_user = sql_call_fetch_one('updateUserEmail', (user['userId'], email))
        
        if not updated_user:
            return make_response(jsonify({'status': 'error', 'message': 'Failed to update email'}), 500)
        
        from app.utils.helpers import generate_otp
        otp = generate_otp()
        
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
        
        parser = reqparse.RequestParser()
        parser.add_argument('phone', type=str, required=True, help='Phone number is required')
        args = parser.parse_args()
        
        # Sanitize
        phone = sanitize_string(args['phone'])
        
        if not phone:
            return make_response(jsonify({'status': 'error', 'message': 'Phone number is required after sanitization'}), 400)
        
        # Validate phone number
        if not phone.startswith('+') or not phone[1:].isdigit():
            return make_response(jsonify({'status': 'error', 'message': 'Phone number must be in format (e.g., +1234567890)'}), 400)
        
        username = session['username']
        user = sql_call_fetch_one('getUserByUsername', (username,))
        
        if not user:
            return make_response(jsonify({'status': 'error', 'message': 'User not found'}), 404)
        
        if 'phone_number' not in user:
            return make_response(jsonify({
                'status': 'error',
                'message': 'Phone number functionality is not available. The database needs to be updated.'
            }), 400)
        
        # Check if the new phone number is the same as the current one
        if user.get('phone_number') and user['phone_number'] == phone:
            return make_response(jsonify({'status': 'error', 'message': 'The phone number is the same as your current one'}), 400)
        
        updated_user = sql_call_fetch_one('updateUserPhone', (user['userId'], phone))
        
        if not updated_user:
            return make_response(jsonify({'status': 'error', 'message': 'Failed to update phone number'}), 500)
        
        from app.utils.helpers import generate_otp
        otp = generate_otp()
        
        # Store OTP
        sql_call_fetch_one('createMobileVerification', (updated_user['userId'], otp))
        
        # Check if SMS is enabled
        from app.services.sms_service import send_verification_sms, is_sms_enabled
        sms_sent = False
        if is_sms_enabled():
            sms_sent = send_verification_sms(phone, updated_user['username'], otp)

        response_data = {**updated_user, 'sms_sent': sms_sent}
        
        return make_response(jsonify(response_data), 200)
    
class UserBlogList(Resource):
    def get(self, userId):
        # Check if user exists
        user = sql_call_fetch_one('getUserById', (userId,))
        if not user:
            return make_response(jsonify({'status': 'error', 'message': 'User not found'}), 404)
        newer_than = request.args.get('newerThan')
        limit = request.args.get('limit', default=20, type=int)
        offset = request.args.get('offset', default=0, type=int)

        if newer_than:
            try:
                from datetime import datetime
                newer_than = datetime.strptime(newer_than, '%Y-%m-%d').date()
            except ValueError:
                return make_response(jsonify({'status': 'error', 'message': 'Invalid date format. Use YYYY-MM-DD'}), 400)
        
        # Get blogs
        blogs = sql_call_fetch_all('getBlogsByUserId', (userId, newer_than, limit, offset))
        
        response = make_response(jsonify(blogs), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    
class UserNotificationPreferences(Resource):
    @login_required
    def get(self):
        # Get user
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
        
        parser = reqparse.RequestParser()
        parser.add_argument('notifyOnBlog', type=bool, required=True, help='notifyOnBlog is required')
        parser.add_argument('notifyOnComment', type=bool, required=True, help='notifyOnComment is required')
        args = parser.parse_args()
        
        # Get user
        username = session['username']
        user = sql_call_fetch_one('getUserByUsername', (username,))
        
        if not user:
            return make_response(jsonify({'status': 'error', 'message': 'User not found'}), 404)
        
        # Update notification preferenc
        prefs = sql_call_fetch_one('updateNotificationPreferences', (
            user['userId'], 
            args['notifyOnBlog'],
            args['notifyOnComment']
        ))
        
        if not prefs:
            return make_response(jsonify({'status': 'error', 'message': 'Failed to update notification preferences'}), 500)
        
        return make_response(jsonify(prefs), 200)