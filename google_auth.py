from flask import redirect, url_for, session, flash, request, current_app
from oauthlib.oauth2 import WebApplicationClient
import requests
from oauth_config import init_oauth_client, get_google_provider_cfg, get_google_auth_url, get_google_token, get_google_user_info
from datetime import datetime

def init_google_auth(app):
    """Initialize Google OAuth configuration"""
    app.config['GOOGLE_CLIENT_ID'] = app.config.get('GOOGLE_CLIENT_ID', 'your-client-id')
    app.config['GOOGLE_CLIENT_SECRET'] = app.config.get('GOOGLE_CLIENT_SECRET', 'your-client-secret')
    app.config['GOOGLE_DISCOVERY_URL'] = "https://accounts.google.com/.well-known/openid-configuration"
    app.oauth_client = init_oauth_client()

def handle_google_login(users):
    """Handle Google OAuth Sign-In"""
    client = current_app.oauth_client
    base_url = request.base_url.rsplit('/', 1)[0]
    authorization_url = get_google_auth_url(client, base_url)
    if authorization_url:
        return redirect(authorization_url)
    else:
        flash("Failed to get Google authorization URL", "error")
        return redirect(url_for('login.login'))

def handle_google_callback(users):
    """Handle Google OAuth callback"""
    client = current_app.oauth_client
    base_url = request.base_url.rsplit('/', 1)[0]

    code = request.args.get('code')
    if not code:
        flash("Authorization code not found", "error")
        return redirect(url_for('login.login'))

    token_response = get_google_token(client, base_url, request.url)
    if not token_response:
        error_description = request.args.get('error_description', 'No error description provided')
        flash(f"Failed to get token from Google: {error_description}", "error")
        return redirect(url_for('login.login'))

    user_info = get_google_user_info(client, token_response)
    if not user_info:
        flash("Failed to get user info from Google", "error")
        return redirect(url_for('login.login'))

    email = user_info.get('email')
    name = user_info.get('name')
    picture = user_info.get('picture')

    # Check if user exists
    existing_user = None
    for username, user in users.items():
        if user.get('email') == email:
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
            'email': email,
            'name': name,
            'picture': picture,
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
