#!/usr/bin/env python3
from app import create_app

app = create_app()

if __name__ == "__main__":
    context = ('cert.pem', 'key.pem')
    app.run(
        host=app.config['APP_HOST'],
        port=app.config['APP_PORT'],
        ssl_context=context,
        debug=app.config['APP_DEBUG']
    )