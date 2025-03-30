from flask import request, session, make_response, jsonify
from flask_restful import Resource
from datetime import datetime

from app.services.db_service import sql_call_fetch_one, sql_call_fetch_all
from app.services.email_service import send_blog_notification
from app.utils.helpers import sanitize_string, sanitize_html
from app.utils.decorators import login_required, verification_required, ownership_required

class BlogList(Resource):
    def get(self):
        newer_than = request.args.get('newerThan')
        author = request.args.get('author')
        limit = request.args.get('limit', default=20, type=int)
        offset = request.args.get('offset', default=0, type=int)
        
        if newer_than:
            try:
                newer_than = datetime.strptime(newer_than, '%Y-%m-%d').date()
            except ValueError:
                return make_response(jsonify({'status': 'error', 'message': 'Invalid date format. Use YYYY-MM-DD'}), 400)
        
        # Sanitize author input
        author = sanitize_string(author) if author else None
        
        blogs = sql_call_fetch_all('getBlogs', (newer_than, author, limit, offset))
        
        return make_response(jsonify(blogs), 200)

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
        data = request.get_json()
        if not data or 'title' not in data or 'content' not in data:
            return make_response(jsonify({'status': 'error', 'message': 'Title and content are required'}), 400)
        
        # Sanitize inputs
        title = sanitize_string(data['title'])
        content = sanitize_html(data['content'])
        
        if not title or not content:
            return make_response(jsonify({'status': 'error', 'message': 'Title and content are required after sanitization'}), 400)
        
        username = session['username']
        user = sql_call_fetch_one('getUserByUsername', (username,))
        
        blog = sql_call_fetch_one('createBlog', (title, content, user['userId']))
        
        subscribers = [u['email'] for u in sql_call_fetch_all('getUsers', (1000, 0))
                       if u['userId'] != user['userId'] and u['email'] and sql_call_fetch_one('getUserNotificationPreferences', (u['userId'],)).get('notifyOnBlog')]
        
        if subscribers:
            send_blog_notification(blog, user['username'], subscribers)
        
        return make_response(jsonify(blog), 201)

class BlogUpdate(Resource):
    @login_required
    @verification_required
    @ownership_required('blog')
    def put(self, blogId):
        data = request.get_json()
        if not data or 'title' not in data or 'content' not in data:
            return make_response(jsonify({'status': 'error', 'message': 'Title and content are required'}), 400)
        
        title = sanitize_string(data['title'])
        content = sanitize_html(data['content'])
        
        username = session['username']
        user = sql_call_fetch_one('getUserByUsername', (username,))
        
        blog = sql_call_fetch_one('updateBlog', (blogId, title, content, user['userId']))
        
        if not blog:
            return make_response(jsonify({'status': 'error', 'message': 'Blog not found or not updated'}), 404)
        
        return make_response(jsonify(blog), 200)

class BlogDelete(Resource):
    @login_required
    @verification_required
    @ownership_required('blog')
    def delete(self, blogId):
        username = session['username']
        user = sql_call_fetch_one('getUserByUsername', (username,))
        
        result = sql_call_fetch_one('deleteBlog', (blogId, user['userId']))
        
        if not result or result['affectedRows'] == 0:
            return make_response(jsonify({'status': 'error', 'message': 'Blog not found or not deleted'}), 404)
        
        return make_response('', 204)
