from flask import redirect, url_for, session, flash
import os
import json
from datetime import datetime
import requests

def init_google_auth(app):
    """Initialize Google OAuth configuration"""
    app.config['GOOGLE_CLIENT_ID'] = os.getenv('GOOGLE_CLIENT_ID', 'your-client-id')
    app.config['GOOGLE_CLIENT_SECRET'] = os.getenv('GOOGLE_CLIENT_SECRET', 'your-client-secret')
    app.config['GOOGLE_DISCOVERY_URL'] = "https://accounts.google.com/.well-known/openid-configuration"

def handle_google_login(users):
    """Handle Google OAuth Sign-In"""
    try:
        # For development mode, simulate Google OAuth
        if not os.getenv('GOOGLE_CLIENT_ID'):
            # Simulate Google user data
            google_data = {
                'email': 'test.google@example.com',
                'name': 'Test Google User',
                'picture': 'https://lh3.googleusercontent.com/test_photo'
            }
            
            # Check if user exists
            existing_user = None
            for username, user in users.items():
                if user.get('email') == google_data['email']:
                    existing_user = username
                    break

            if existing_user:
                # Log in existing user
                session['logged_in'] = True
                session['username'] = existing_user
                session['is_admin'] = False
                session['registered_on'] = users[existing_user]['registered_on']
                flash('Successfully signed in with Google!', 'success')
                return redirect(url_for('index'))
            else:
                # Create new user with Google data
                username = f"google_user_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                users[username] = {
                    'email': google_data['email'],
                    'name': google_data['name'],
                    'picture': google_data['picture'],
                    'google_auth': True,
                    'verified': True,
                    'registered_on': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # Log in new user
                session['logged_in'] = True
                session['username'] = username
                session['is_admin'] = False
                session['registered_on'] = users[username]['registered_on']
                flash('Successfully created account with Google!', 'success')
                return redirect(url_for('index'))
        
        # In production, implement actual Google OAuth flow
        flash("Google Sign-In is not configured", "error")
        return redirect(url_for('login'))
        
    except Exception as e:
        flash(f"Error during Google authentication: {str(e)}", "error")
        return redirect(url_for('login'))
