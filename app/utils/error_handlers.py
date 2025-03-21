from flask import make_response, jsonify

def register_error_handlers(app):
    """Register error handlers for the Flask app"""
    
    @app.errorhandler(400)
    def bad_request(error):
        return make_response(jsonify({'status': 'error', 'message': 'Bad request'}), 400)

    @app.errorhandler(401)
    def unauthorized(error):
        return make_response(jsonify({'status': 'error', 'message': 'Unauthorized'}), 401)

    @app.errorhandler(403)
    def forbidden(error):
        return make_response(jsonify({'status': 'error', 'message': 'Access denied'}), 403)

    @app.errorhandler(404)
    def not_found(error):
        return make_response(jsonify({'status': 'error', 'message': 'Resource not found'}), 404)

    @app.errorhandler(405)
    def method_not_allowed(error):
        return make_response(jsonify({'status': 'error', 'message': 'Method not allowed'}), 405)

    @app.errorhandler(500)
    def server_error(error):
        return make_response(jsonify({'status': 'error', 'message': 'Server error'}), 500)