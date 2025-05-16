#!/usr/bin/env python3
"""
Development server script for testing Vercel deployment locally.
"""
import os

# Set environment variables for Vercel-like environment
os.environ['VERCEL'] = '1'
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = '1'

from api.index import app

if __name__ == "__main__":
    # Initialize the database
    with app.app_context():
        from app.database import db
        db.create_all()
    
    # Run the Flask development server
    app.run(debug=True, port=3000)
