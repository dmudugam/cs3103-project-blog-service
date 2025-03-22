from flask import request, jsonify, make_response
from flask_restful import Resource, reqparse

from app.services.ai_service import generate_content
from app.utils.decorators import login_required, verification_required

class GeminiAI(Resource):
    @login_required
    @verification_required
    def post(self):
        if not request.is_json:
            return make_response(jsonify({'status': 'error', 'message': 'Request must be JSON'}), 400)
        
        # Parse request
        parser = reqparse.RequestParser()
        parser.add_argument('prompt', type=str, required=True, help='Prompt is required')
        parser.add_argument('mode', type=str, required=False, default='generate', 
                           help='Mode: generate (new content) or enhance (improve existing)')
        parser.add_argument('content', type=str, required=False, 
                           help='Content to enhance (required if mode is enhance)')
        args = parser.parse_args()
        
        # Validate input
        if args['mode'] == 'enhance' and not args['content']:
            return make_response(jsonify({
                'status': 'error', 
                'message': 'Content is required when mode is enhance'
            }), 400)
        
        # Call Gemini AI service
        result = generate_content(args['prompt'], args['mode'], args['content'])
        
        # Return response
        if result.get('status') == 'success':
            return jsonify({
                'status': 'success',
                'generatedContent': result.get('generatedContent')
            })
        else:
            return make_response(jsonify(result), 500)