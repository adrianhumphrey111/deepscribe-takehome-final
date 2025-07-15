import os
from flask import send_from_directory, send_file
from werkzeug.exceptions import NotFound

def setup_static_routes(app):
    """Set up static file serving for Next.js build"""
    
    # Path to Next.js build output
    static_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'out')
    
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_static(path):
        """Serve static files from Next.js build"""
        try:
            if path == '' or path == 'index.html':
                return send_file(os.path.join(static_folder, 'index.html'))
            
            # Try to serve the file directly
            if os.path.exists(os.path.join(static_folder, path)):
                return send_from_directory(static_folder, path)
            
            # If it's a directory, try to serve index.html from it
            if os.path.exists(os.path.join(static_folder, path, 'index.html')):
                return send_file(os.path.join(static_folder, path, 'index.html'))
            
            # For SPA routing, serve index.html for non-API routes
            if not path.startswith('api/'):
                return send_file(os.path.join(static_folder, 'index.html'))
            
            # If nothing else works, 404
            raise NotFound()
            
        except Exception as e:
            # Fallback to index.html for SPA routing
            if not path.startswith('api/'):
                return send_file(os.path.join(static_folder, 'index.html'))
            raise NotFound()