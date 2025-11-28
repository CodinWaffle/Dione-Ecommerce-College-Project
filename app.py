#!/usr/bin/env python3
# Flask application with database saving functionality
"""
Simple entry point for Dione Ecommerce
Can be run with: python app.py
Or with Flask CLI: flask run
"""

from project import create_app, db

# Create the Flask application
app = create_app('development')

# Create database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    print("Starting Dione Ecommerce")
    print("Server: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)

