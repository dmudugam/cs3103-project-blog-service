from flask import Flask, request, render_template
from flask import send_from_directory
from flask_restful import Api
from flask_session import Session
from flask_cors import CORS
import json
from datetime import datetime, date, timedelta
import os
import sys

def create_app():
    app = Flask(__name__, static_folder='../static', template_folder='../templates')
    
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
    
    Session(app)
    
    class JSONEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            return super(JSONEncoder, self).default(obj)
    
    app.json_encoder = JSONEncoder
    
    api = Api(app)
    
    from app.utils.error_handlers import register_error_handlers
    register_error_handlers(app)
    
    # Import and register routes
    from app.routes import register_routes
    register_routes(api)
    
    @app.after_request
    def after_request(response):
        # Set content type for JSON responses
        if not response.headers.get('Content-Type'):
            response.headers['Content-Type'] = 'application/json'
        
        # CORS headers
        response.headers.setdefault('Access-Control-Allow-Origin', f"https://{app.config['APP_HOST']}")
        response.headers.setdefault('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.setdefault('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.setdefault('Access-Control-Allow-Credentials', 'true')
        
        return response


    @app.route('/')
    def serve_index():
        return send_from_directory('../templates', 'index.html')
    
    @app.route('/docs/<path:filename>')
    def serve_docs(filename):
        docs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'docs')
        return send_from_directory(docs_dir, filename)
    
    return app