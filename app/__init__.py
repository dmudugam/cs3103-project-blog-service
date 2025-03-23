from flask import Flask, request
from flask import send_from_directory
from flask_restful import Api
from flask_session import Session
from flask_cors import CORS
import json
from datetime import datetime, date, timedelta
import os
import sys

# Import routes aftr app initialization
def create_app():
    app = Flask(__name__, static_folder='../static', template_folder='../templates')
    
    # Load configuration
    app.config.from_pyfile(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'settings.py'))
    
    # Session configuration
    app.secret_key = app.config['SECRET_KEY']
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_COOKIE_NAME'] = 'peanutButter'
    app.config['SESSION_COOKIE_DOMAIN'] = app.config['APP_HOST']
    app.config['SESSION_COOKIE_SAMESITE'] = 'None'
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
    
    # Initialize CORS (because browsers are paranoid and need therapy about sharing :P)
    CORS(app, resources={r"/*": {"origins": f"https://{app.config['APP_HOST']}", "supports_credentials": True}})
    
    # Initialize session
    Session(app)
    
    # Format date
    class JSONEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            return super(JSONEncoder, self).default(obj)
    
    app.json_encoder = JSONEncoder
    
    # Initialize API
    api = Api(app)
    
    # Import and register error handlers
    from app.utils.error_handlers import register_error_handlers
    register_error_handlers(app)
    
    # Import and register routes
    from app.routes import register_routes
    register_routes(api)
    
    @app.after_request
    def after_request(response):
        """Ensure all responses have appropriate headers"""
        # Set content type for JSON responses
        if request.path.startswith('/blogs') or request.path.startswith('/users') or request.path.startswith('/comments'):
            response.headers.setdefault('Content-Type', 'application/json')
        
        # CORS headers
        response.headers.setdefault('Access-Control-Allow-Origin', f"https://{app.config['APP_HOST']}")
        response.headers.setdefault('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.setdefault('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.setdefault('Access-Control-Allow-Credentials', 'true')
        
        return response
    
    # Add direct route handlers
    from app.routes.direct_routes import register_direct_routes
    register_direct_routes(app)

    @app.route('/')
    def serve_index():
        return send_from_directory('../templates', 'index.html')
    
    return app