from functools import wraps
from flask import session, make_response, jsonify
from app.services.db_service import sql_call_fetch_one

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return make_response(jsonify({'status': 'error', 'message': 'Authentication required'}), 401)
        return f(*args, **kwargs)
    return decorated_function

def verification_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return make_response(jsonify({'status': 'error', 'message': 'Authentication required'}), 401)
        
        # Get user ID from session
        username = session['username']
        user = sql_call_fetch_one('getUserByUsername', (username,))
        if not user:
            return make_response(jsonify({'status': 'error', 'message': 'User not found'}), 404)
        
        # Check if user is verified by either email or mobile
        is_verified = user.get('verified', False)
        is_mobile_verified = user.get('mobile_verified', False)
        
        if not (is_verified or is_mobile_verified):
            return make_response(jsonify({
                'status': 'error', 
                'message': 'Verification required. Please verify either your email or phone number.'
            }), 403)
        
        return f(*args, **kwargs)
    return decorated_function

def ownership_required(resource_type):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'username' not in session:
                return make_response(jsonify({'status': 'error', 'message': 'Authentication required'}), 401)
            
            # Get user ID from session
            username = session['username']
            user = sql_call_fetch_one('getUserByUsername', (username,))
            if not user:
                return make_response(jsonify({'status': 'error', 'message': 'User not found'}), 404)
            
            user_id = user['userId']
            
            # Check ownership based on resource type
            if resource_type == 'blog':
                blog_id = kwargs.get('blogId')
                if not blog_id:
                    return make_response(jsonify({'status': 'error', 'message': 'Blog ID required'}), 400)
                
                # Get blog
                blog = sql_call_fetch_one('getBlogById', (blog_id,))
                if not blog:
                    return make_response(jsonify({'status': 'error', 'message': 'Blog not found'}), 404)
                
                # Check if user is the owner
                if blog['userId'] != user_id:
                    return make_response(jsonify({'status': 'error', 'message': 'You do not have permission to modify this blog'}), 403)
            
            elif resource_type == 'comment':
                comment_id = kwargs.get('commentId')
                if not comment_id:
                    return make_response(jsonify({'status': 'error', 'message': 'Comment ID required'}), 400)
                
                # Get comment
                comment = sql_call_fetch_one('getCommentById', (comment_id,))
                if not comment:
                    return make_response(jsonify({'status': 'error', 'message': 'Comment not found'}), 404)
                
                # Check if user is the owner
                if comment['userId'] != user_id:
                    return make_response(jsonify({'status': 'error', 'message': 'You do not have permission to modify this comment'}), 403)
            
            # Continue if ownership check passes
            return f(*args, **kwargs)
        return decorated_function
    return decorator