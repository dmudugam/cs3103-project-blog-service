from flask import request, session, make_response, jsonify
from flask_restful import Resource, reqparse

from app.services.db_service import sql_call_fetch_one, sql_call_fetch_all
from app.services.email_service import send_blog_notification
from app.utils.helpers import sanitize_string, sanitize_html
from app.utils.decorators import login_required, verification_required, ownership_required

class BlogList(Resource):
    def get(self):
        # Parse query parameters
        parser = reqparse.RequestParser()
        parser.add_argument('newerThan', type=str, required=False, help='Filter blogs created after this date (YYYY-MM-DD)')
        parser.add_argument('author', type=str, required=False, help='Filter blogs by author name')
        parser.add_argument('limit', type=int, required=False, default=20, help='Maximum number of blogs to return')
        parser.add_argument('offset', type=int, required=False, default=0, help='Number of blogs to skip for pagination')
        args = parser.parse_args()
        
        # Convert date string to date object if provided
        newer_than = None
        if args['newerThan']:
            try:
                from datetime import datetime
                newer_than = datetime.strptime(args['newerThan'], '%Y-%m-%d').date()
            except ValueError:
                return make_response(jsonify({'status': 'error', 'message': 'Invalid date format. Use YYYY-MM-DD'}), 400)
        
        # Sanitize author input
        author = sanitize_string(args['author']) if args['author'] else None
        
        # Get blogs from database
        blogs = sql_call_fetch_all('getBlogs', (newer_than, author, args['limit'], args['offset']))
        
        # Set response headers
        response = make_response(jsonify(blogs), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

class BlogDetail(Resource):
    def get(self, blogId):
        blog = sql_call_fetch_one('getBlogById', (blogId,))
        if not blog:
            return make_response(jsonify({'status': 'error', 'message': 'Blog not found'}), 404)
        
        return make_response(jsonify(blog), 200)

class BlogCreate(Resource):
    @login_required
    @verification_required
    def post(self):
        if not request.json:
            return make_response(jsonify({'status': 'error', 'message': 'No JSON data provided'}), 400)
        
        # Parse request
        parser = reqparse.RequestParser()
        parser.add_argument('title', type=str, required=True, help='Title is required')
        parser.add_argument('content', type=str, required=True, help='Content is required')
        args = parser.parse_args()
        
        # Sanitize inputs
        title = sanitize_string(args['title'])
        content = sanitize_html(args['content'])
        
        if not title or not content:
            return make_response(jsonify({'status': 'error', 'message': 'Title and content are required after sanitization'}), 400)
        
        # Get user ID from session
        username = session['username']
        user = sql_call_fetch_one('getUserByUsername', (username,))
        
        # Create blog
        blog = sql_call_fetch_one('createBlog', (title, content, user['userId']))
        
        subscribers = []
        users = sql_call_fetch_all('getUsers', (1000, 0))
        
        for potential_subscriber in users:
            if potential_subscriber['userId'] != user['userId'] and potential_subscriber['email']:
                # Check if user wants blog notifications
                prefs = sql_call_fetch_one('getUserNotificationPreferences', (potential_subscriber['userId'],))
                if prefs and prefs['notifyOnBlog']:
                    subscribers.append(potential_subscriber['email'])
        
        # Send notification email
        if subscribers:
            send_blog_notification(blog, user['username'], subscribers)
        
        return make_response(jsonify(blog), 201)

class BlogUpdate(Resource):
    @login_required
    @verification_required
    @ownership_required('blog')
    def put(self, blogId):
        if not request.json:
            return make_response(jsonify({'status': 'error', 'message': 'No JSON data provided'}), 400)
        
        # Parse request
        parser = reqparse.RequestParser()
        parser.add_argument('title', type=str, required=True, help='Title is required')
        parser.add_argument('content', type=str, required=True, help='Content is required')
        args = parser.parse_args()
        
        # Sanitize inputs
        title = sanitize_string(args['title'])
        content = sanitize_html(args['content'])
        
        if not title or not content:
            return make_response(jsonify({'status': 'error', 'message': 'Title and content are required after sanitization'}), 400)
        
        # Get user ID from session
        username = session['username']
        user = sql_call_fetch_one('getUserByUsername', (username,))
        
        # Update blog
        blog = sql_call_fetch_one('updateBlog', (blogId, title, content, user['userId']))
        
        if not blog:
            return make_response(jsonify({'status': 'error', 'message': 'Blog not found or not updated'}), 404)
        
        return make_response(jsonify(blog), 200)

class BlogDelete(Resource):
    @login_required
    @verification_required
    @ownership_required('blog')
    def delete(self, blogId):
        # Get user ID from session
        username = session['username']
        user = sql_call_fetch_one('getUserByUsername', (username,))
        
        # Delete blog
        result = sql_call_fetch_one('deleteBlog', (blogId, user['userId']))
        
        if not result or result['affectedRows'] == 0:
            return make_response(jsonify({'status': 'error', 'message': 'Blog not found or not deleted'}), 404)
        
        return make_response('', 204)