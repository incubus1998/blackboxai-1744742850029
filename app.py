from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for, flash, session
from dotenv import load_dotenv
load_dotenv()

import os
import json
from datetime import datetime, timedelta
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import AskAIAssignment
import requests
from login import init_login
from google_auth import init_google_auth, handle_google_login

app = Flask(__name__)

# Log Google OAuth environment variables at startup
import logging
import os
client_id = os.getenv('GOOGLE_CLIENT_ID')
client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
if client_id and client_secret and client_id != "your-client-id" and client_secret != "your-client-secret":
    logging.info(f"Google OAuth Client ID is set: {client_id[:5]}***")
else:
    logging.warning("Google OAuth Client ID or Client Secret is not set or using default placeholders!")

@app.route('/debug-oauth-config')
def debug_oauth_config():
    import os
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    return f"GOOGLE_CLIENT_ID: {client_id}<br>GOOGLE_CLIENT_SECRET: {client_secret}"

# Configuration
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config.update(
    UPLOAD_FOLDER='uploads',
    MAX_CONTENT_LENGTH=10 * 1024 * 1024,  # 10MB max file size
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=1800  # 30 minutes
)

# Create upload folder if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# User storage (replace with database in production)
users = {}
verification_codes = {}

# Load environment variables explicitly for Google OAuth
app.config['GOOGLE_CLIENT_ID'] = os.getenv('GOOGLE_CLIENT_ID')
app.config['GOOGLE_CLIENT_SECRET'] = os.getenv('GOOGLE_CLIENT_SECRET')

# Initialize Google OAuth and Login Blueprint
init_google_auth(app)
login_blueprint = init_login(users)
app.register_blueprint(login_blueprint)

# Add main routes for pages
@app.before_request
def log_request_info():
    app.logger.info(f"Request URL: {request.url}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/index.html')
def index_html():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/login.html')
def login_html():
    return render_template('login.html')

@app.route('/ai_assignment_helper')
def ai_assignment_helper():
    return render_template('ai_assignment_helper.html')

@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')

@app.route('/robots.txt')
def robots():
    return app.send_static_file('robots.txt')

# 404 error handler
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404

# Catch-all route to log unknown URLs for debugging
@app.route('/<path:unknown_path>')
def catch_all(unknown_path):
    app.logger.warning(f"404 Not Found: /{unknown_path}")
    return render_template('error.html'), 404

# The rest of the code remains unchanged

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
