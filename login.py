from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime

login_bp = Blueprint('login', __name__)

def init_login(users_dict):
    """Initialize login blueprint with users dictionary"""
    
    @login_bp.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')

            # Validate input
            if not all([email, password]):
                flash('All fields are required', 'error')
                return render_template('login.html', signup=False)

            # Find user by email
            user_found = None
            for username, user in users_dict.items():
                if user.get('email') == email:
                    user_found = (username, user)
                    break

            if user_found and user_found[1]['password'] == password:  # In production, use proper password hashing
                username, user = user_found
                session['logged_in'] = True
                session['username'] = username
                session['is_admin'] = False
                session['registered_on'] = user['registered_on']
                flash('Login successful!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid email or password', 'error')
                return render_template('login.html', signup=False)

        return render_template('login.html', signup=False)

    @login_bp.route('/logout')
    def logout():
        session.clear()
        flash('Successfully logged out!', 'success')
        return redirect(url_for('login.login'))

    return login_bp
