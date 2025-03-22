from flask import request, session, make_response, jsonify
from flask_restful import Resource, reqparse

from app.services.db_service import sql_call_fetch_one, sql_call_fetch_all
from app.services.email_service import send_comment_notification
from app.utils.helpers import sanitize_html
from app.utils.decorators import login_required, verification_required, ownership_required

class BlogCommentList(Resource):
    def get(self, blogId):
        # Parse query parameters
        parser = reqparse.RequestParser()
        parser.add_argument('newerThan', type=str, required=False, help='Filter comments created after this date (YYYY-MM-DD)')
        parser.add_argument('limit', type=int, required=False, default=20, help='Maximum number of comments to return')
        parser.add_argument('offset', type=int, required=False, default=0, help='Number of comments to skip for pagination')
        args = parser.parse_args()
        
        # Convert date string to date object if provided
        newer_than = None
        if args['newerThan']:
            try:
                from datetime import datetime
                newer_than = datetime.strptime(args['newerThan'], '%Y-%m-%d').date()
            except ValueError:
                return make_response(jsonify({'status': 'error', 'message': 'Invalid date format. Use YYYY-MM-DD'}), 400)
        
        # Get comments from database
        comments = sql_call_fetch_all('getCommentsByBlog', (blogId, newer_than, args['limit'], args['offset']))
        
        response = make_response(jsonify(comments), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

class BlogCommentCreate(Resource):
    @login_required
    @verification_required
    def post(self, blogId):
        if not request.json:
            return make_response(jsonify({'status': 'error', 'message': 'No JSON data provided'}), 400)
        
        # Check if blog exists
        blog = sql_call_fetch_one('getBlogById', (blogId,))
        if not blog:
            return make_response(jsonify({'status': 'error', 'message': 'Blog not found'}), 404)
        
        # Parse request
        parser = reqparse.RequestParser()
        parser.add_argument('content', type=str, required=True, help='Content is required')
        args = parser.parse_args()
        
        # Sanitize content
        content = sanitize_html(args['content'])
        
        if not content:
            return make_response(jsonify({'status': 'error', 'message': 'Content is required after sanitization'}), 400)
        
        # Get user ID from session
        username = session['username']
        user = sql_call_fetch_one('getUserByUsername', (username,))
        
        # Create comment
        comment = sql_call_fetch_one('createComment', (content, user['userId'], blogId, None))
        
        # Get blog author for notification
        blog_author = sql_call_fetch_one('getUserById', (blog['userId'],))
        
        if blog_author and blog_author['email']:
            # Check if author wants comment notifications
            prefs = sql_call_fetch_one('getUserNotificationPreferences', (blog_author['userId'],))
            if prefs and prefs['notifyOnComment']:
                send_comment_notification(comment, blog['title'], user['username'], blog_author['email'])
        
        return make_response(jsonify(comment), 201)

class CommentDetail(Resource):
    def get(self, commentId):
        comment = sql_call_fetch_one('getCommentById', (commentId,))
        if not comment:
            return make_response(jsonify({'status': 'error', 'message': 'Comment not found'}), 404)
        
        return make_response(jsonify(comment), 200)

class CommentUpdate(Resource):
    @login_required
    @verification_required
    @ownership_required('comment')
    def put(self, commentId):
        if not request.json:
            return make_response(jsonify({'status': 'error', 'message': 'No JSON data provided'}), 400)
        
        # Parse request
        parser = reqparse.RequestParser()
        parser.add_argument('content', type=str, required=True, help='Content is required')
        args = parser.parse_args()
        
        # Sanitize content
        content = sanitize_html(args['content'])
        
        if not content:
            return make_response(jsonify({'status': 'error', 'message': 'Content is required after sanitization'}), 400)
        
        # Get user ID from session
        username = session['username']
        user = sql_call_fetch_one('getUserByUsername', (username,))
        
        # Update comment
        comment = sql_call_fetch_one('updateComment', (commentId, content, user['userId']))
        
        if not comment:
            return make_response(jsonify({'status': 'error', 'message': 'Comment not found or not updated'}), 404)
        
        return make_response(jsonify(comment), 200)

class CommentDelete(Resource):
    @login_required
    @verification_required
    @ownership_required('comment')
    def delete(self, commentId):
        # Get user ID from session
        username = session['username']
        user = sql_call_fetch_one('getUserByUsername', (username,))
        
        # Delete comment
        result = sql_call_fetch_one('deleteComment', (commentId, user['userId']))
        
        if not result or result['affectedRows'] == 0:
            return make_response(jsonify({'status': 'error', 'message': 'Comment not found or not deleted'}), 404)
        
        return make_response('', 204)

class CommentReplyList(Resource):
    def get(self, commentId):
        # Check if comment exists
        comment = sql_call_fetch_one('getCommentById', (commentId,))
        if not comment:
            return make_response(jsonify({'status': 'error', 'message': 'Comment not found'}), 404)
        
        # Get replies from database
        replies = sql_call_fetch_all('getCommentReplies', (commentId,))
        
        response = make_response(jsonify(replies), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

class CommentReplyCreate(Resource):
    @login_required
    @verification_required
    def post(self, commentId):
        if not request.json:
            return make_response(jsonify({'status': 'error', 'message': 'No JSON data provided'}), 400)
        
        # Check if comment exists
        comment = sql_call_fetch_one('getCommentById', (commentId,))
        if not comment:
            return make_response(jsonify({'status': 'error', 'message': 'Comment not found'}), 404)
        
        # Parse request
        parser = reqparse.RequestParser()
        parser.add_argument('content', type=str, required=True, help='Content is required')
        args = parser.parse_args()
        
        # Sanitize content
        content = sanitize_html(args['content'])
        
        if not content:
            return make_response(jsonify({'status': 'error', 'message': 'Content is required after sanitization'}), 400)
        
        # Get user ID from session
        username = session['username']
        user = sql_call_fetch_one('getUserByUsername', (username,))
        
        # Create reply
        reply = sql_call_fetch_one('createComment', (content, user['userId'], comment['blogId'], commentId))
        
        # Notify the original comment author
        comment_author = sql_call_fetch_one('getUserById', (comment['userId'],))
        
        if comment_author and comment_author['email'] and comment_author['userId'] != user['userId']:
            # Check if author wants comment notifications
            prefs = sql_call_fetch_one('getUserNotificationPreferences', (comment_author['userId'],))
            if prefs and prefs['notifyOnComment']:
                # Get blog title
                blog = sql_call_fetch_one('getBlogById', (comment['blogId'],))
                blog_title = blog['title'] if blog else "Unknown Blog"
                
                send_comment_notification(reply, blog_title, user['username'], comment_author['email'])
        
        return make_response(jsonify(reply), 201)