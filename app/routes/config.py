from flask import current_app, jsonify
from flask_restful import Resource

class AppConfig(Resource):
    def get(self):
        return jsonify({
            'host': current_app.config['APP_HOST'],
            'port': current_app.config['APP_PORT'],
            'baseURL': f"https://{current_app.config['APP_HOST']}:{current_app.config['APP_PORT']}"
        })