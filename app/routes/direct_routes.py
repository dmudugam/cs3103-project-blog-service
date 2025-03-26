# from flask import jsonify, request, make_response
# from datetime import datetime
# from app.services.db_service import sql_call_fetch_all, sql_call_fetch_one
# from app.utils.helpers import sanitize_string

# def register_direct_routes(app):
#     """Register direct route handlers (without using Flask-RESTful)"""
    
#     @app.route('/blogs', methods=['GET'])
#     def get_all_blogs():
#         """Direct route handler for blogs endpoint"""
#         # Parse query parameters
#         newer_than = request.args.get('newerThan')
#         author = request.args.get('author')
#         limit = request.args.get('limit', 20, type=int)
#         offset = request.args.get('offset', 0, type=int)
        
#         # Convert date string to date object if provided
#         newer_than_date = None
#         if newer_than:
#             try:
#                 newer_than_date = datetime.strptime(newer_than, '%Y-%m-%d').date()
#             except ValueError:
#                 return jsonify({'status': 'error', 'message': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
#         # Sanitize author input
#         author = sanitize_string(author) if author else None
        
#         # Get blogs from database
#         blogs = sql_call_fetch_all('getBlogs', (newer_than_date, author, limit, offset))
        
#         # Set response headers
#         response = make_response(jsonify(blogs))
#         response.headers['Content-Type'] = 'application/json'
#         return response

#     @app.route('/users/<int:user_id>/blogs', methods=['GET'])
#     def get_user_blogs(user_id):
#         """Direct route handler for user blogs endpoint"""
#         # Check if user exists
#         user = sql_call_fetch_one('getUserById', (user_id,))
#         if not user:
#             return jsonify({'status': 'error', 'message': 'User not found'}), 404
        
#         # Parse query parameters
#         newer_than = request.args.get('newerThan')
#         limit = request.args.get('limit', 20, type=int)
#         offset = request.args.get('offset', 0, type=int)
        
#         # Convert date string to date object if provided
#         newer_than_date = None
#         if newer_than:
#             try:
#                 newer_than_date = datetime.strptime(newer_than, '%Y-%m-%d').date()
#             except ValueError:
#                 return jsonify({'status': 'error', 'message': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
#         # Get blogs from database
#         blogs = sql_call_fetch_all('getBlogsByUserId', (user_id, newer_than_date, limit, offset))
        
#         # Set response headers
#         response = make_response(jsonify(blogs))
#         response.headers['Content-Type'] = 'application/json'
#         return response

#     @app.route('/blogs/<int:blog_id>', methods=['GET'])
#     def get_blog_by_id(blog_id):
#         """Direct route handler for blog detail"""
#         blog = sql_call_fetch_one('getBlogById', (blog_id,))
#         if not blog:
#             return jsonify({'status': 'error', 'message': 'Blog not found'}), 404
        
#         # Set response headers
#         response = make_response(jsonify(blog))
#         response.headers['Content-Type'] = 'application/json'
#         return response

#     @app.route('/blogs/<int:blog_id>/comments', methods=['GET'])
#     def get_blog_comments(blog_id):
#         """Direct route handler for blog comments"""
#         # Check if blog exists
#         blog = sql_call_fetch_one('getBlogById', (blog_id,))
#         if not blog:
#             return jsonify({'status': 'error', 'message': 'Blog not found'}), 404
        
#         # Parse query parameters
#         newer_than = request.args.get('newerThan')
#         limit = request.args.get('limit', 20, type=int)
#         offset = request.args.get('offset', 0, type=int)
        
#         # Convert date string to date object if provided
#         newer_than_date = None
#         if newer_than:
#             try:
#                 newer_than_date = datetime.strptime(newer_than, '%Y-%m-%d').date()
#             except ValueError:
#                 return jsonify({'status': 'error', 'message': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
#         # Get comments from database
#         comments = sql_call_fetch_all('getCommentsByBlog', (blog_id, newer_than_date, limit, offset))
        
#         # Set response headers
#         response = make_response(jsonify(comments))
#         response.headers['Content-Type'] = 'application/json'
#         return response