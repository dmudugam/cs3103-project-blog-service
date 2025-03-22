import requests
import json
from flask import current_app
import sys

def generate_content(prompt, mode='generate', content=None):
    """Generate content using the Gemini API"""
    try:
        # Prepare the prompt based on the mode
        if mode == 'enhance' and content:
            full_prompt = f"Improve this blog content while preserving the main ideas: {content}\n\nEnhancement instructions: {prompt}"
        else:
            full_prompt = prompt
        
        # Call Gemini API
        payload = {
            "contents": [{
                "parts": [{"text": full_prompt}]
            }]
        }
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        # Use API key from settings
        url = f"{current_app.config['GEMINI_API_URL']}?key={current_app.config['GEMINI_API_KEY']}"
        
        response = requests.post(url, headers=headers, json=payload)
        response_json = response.json()
        
        # Extract the generated text from Gemini's response
        if 'candidates' in response_json and response_json['candidates']:
            generated_text = response_json['candidates'][0]['content']['parts'][0]['text']
            return {
                'status': 'success',
                'generatedContent': generated_text
            }
        else:
            print(f"Gemini API error: No content generated. Response: {response_json}", file=sys.stderr)
            return {
                'status': 'error',
                'message': 'Failed to generate content',
                'apiResponse': response_json
            }
    except Exception as e:
        print(f"Gemini API error: {e}", file=sys.stderr)
        return {
            'status': 'error',
            'message': f'Error calling Gemini API: {str(e)}'
        }