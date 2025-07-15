#!/usr/bin/env python3
"""
Standalone Flask application runner for backend service
"""
import os
import sys

# Add the current directory to Python path so imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.index import app

if __name__ == '__main__':
    # Set Flask environment
    os.environ['FLASK_ENV'] = os.getenv('FLASK_ENV', 'development')
    os.environ['FLASK_DEBUG'] = '1' if os.environ['FLASK_ENV'] == 'development' else '0'
    
    # Get port from environment or default to 5328
    port = int(os.getenv('PORT', 5328))
    
    print(f"Starting Flask app on port {port}")
    print(f"Environment: {os.environ['FLASK_ENV']}")
    print(f"Debug mode: {os.environ['FLASK_DEBUG']}")
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.environ['FLASK_ENV'] == 'development'
    )