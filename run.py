#!/usr/bin/env python3
from app import create_app
import os

app = create_app()

if __name__ == "__main__":
    # Check if running on Render
    if os.environ.get('RENDER'):
        # Use 0.0.0.0 for production environments
        host = '0.0.0.0'
        port = int(os.environ.get('PORT', 10000))
        app.run(host=host, port=port)
    else:
        # Use configured host/port and SSL for development
        context = ('cert.pem', 'key.pem')
        app.run(
            host=app.config['APP_HOST'],
            port=app.config['APP_PORT'],
            ssl_context=context,
            debug=app.config['APP_DEBUG']
        )