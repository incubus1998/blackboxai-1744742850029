from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for, flash, session
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

# Initialize Google OAuth and Login Blueprint
init_google_auth(app)
login_blueprint = init_login(users)
app.register_blueprint(login_blueprint)

def perform_web_search(query):
    """Perform a web search for the given query."""
    try:
        # This is a placeholder. In a real app, you would use a search API
        results = [
            {
                'title': f'Search result for {query}',
                'snippet': f'This is a sample search result for the query: {query}',
                'url': 'https://example.com'
            }
        ]
        return results
    except Exception as e:
        app.logger.error(f"Error performing web search: {str(e)}")
        return []

def generate_answer_with_web(query, web_results, model):
    """Generate an answer using both the AI model and web search results."""
    try:
        # This is a placeholder. In a real app, you would use the actual AI model
        combined_answer = {
            'answer': f'Combined answer for "{query}" using {model} and web results',
            'sources': [result['url'] for result in web_results],
            'confidence': '95%'
        }
        return combined_answer
    except Exception as e:
        app.logger.error(f"Error generating answer with web: {str(e)}")
        return {'error': 'Failed to generate answer'}

def generate_answer_without_web(query, model):
    """Generate an answer using only the AI model."""
    try:
        # This is a placeholder. In a real app, you would use the actual AI model
        answer = {
            'answer': f'Answer for "{query}" using {model}',
            'confidence': '90%'
        }
        return answer
    except Exception as e:
        app.logger.error(f"Error generating answer: {str(e)}")
        return {'error': 'Failed to generate answer'}

@app.route('/')
def index():
    try:
        # Get query, model, and web search toggle from request args
        query = request.args.get('query', '').strip()
        model = request.args.get('model', '')
        web_search_enabled = request.args.get('web_search', 'false').lower() == 'true'

        if not query:
            return render_template('index.html')

        # Filter models that support web search
        web_search_models = {'gpt40', 'gemini', 'claude37', 'claude35'}
        supports_web_search = model in web_search_models

        # If web search is enabled and model supports it, perform web search
        if web_search_enabled and supports_web_search:
            web_results = perform_web_search(query)
            answer = generate_answer_with_web(query, web_results, model)
        else:
            answer = generate_answer_without_web(query, model)

        return render_template('index.html', query=query, model=model, web_search=web_search_enabled, answer=answer)

    except Exception as e:
        app.logger.error(f"Error rendering index page: {str(e)}")
        return render_template('error.html', error="Failed to load the page"), 500

@app.route('/about')
def about():
    try:
        return render_template('about.html')
    except Exception as e:
        app.logger.error(f"Error rendering about page: {str(e)}")
        return render_template('error.html', error="Failed to load the page"), 500

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    try:
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            message = request.form.get('message')
            
            # Here you would typically save the contact form data or send an email
            # For now, we'll just show a success message
            flash('Thank you for your message! We will get back to you soon.', 'success')
            return redirect(url_for('contact'))
            
        return render_template('contact.html')
    except Exception as e:
        app.logger.error(f"Error processing contact form: {str(e)}")
        return render_template('error.html', error="Failed to process your request"), 500

import random
import string
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# User storage (replace with database in production)
users = {}
verification_codes = {}

def generate_verification_code():
    """Generate a random 6-digit verification code"""
    return ''.join(random.choices(string.digits, k=6))

def send_verification_email(email, code):
    """Send verification email using Gmail SMTP or fallback to console output"""
    try:
        # Get Gmail credentials
        sender_email = os.getenv('GMAIL_USER')
        password = os.getenv('GMAIL_APP_PASSWORD')

        # If credentials are not set, use development mode
        if not sender_email or not password:
            print("\n=== DEVELOPMENT MODE ===")
            print(f"Verification code for {email}: {code}")
            print("======================\n")
            return True

        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = "Verify Your Email - AI Engine"

        # Create HTML content
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #0891b2;">Welcome to AI Engine!</h2>
            <p>Please use this verification code to complete your registration:</p>
            <div style="background-color: #f3f4f6; padding: 20px; text-align: center; border-radius: 8px;">
                <h1 style="color: #0891b2; letter-spacing: 5px;">{code}</h1>
            </div>
            <p>This code will expire in 10 minutes.</p>
            <p style="color: #666; font-size: 12px;">If you didn't request this code, please ignore this email.</p>
        </div>
        """

        msg.attach(MIMEText(html, 'html'))

        # Send email via Gmail SMTP
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.send_message(msg)
            print(f"Verification email sent to {email}")

        return True
    except Exception as e:
        print(f"\nError sending email: {str(e)}")
        print("Falling back to console output:")
        print(f"Verification code for {email}: {code}")
        print("======================\n")
        return True  # Return True so signup process can continue

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Validate input
        if not all([email, username, password]):
            flash('All fields are required', 'error')
            return render_template('signup.html')

        if username in users:
            flash('Username already exists', 'error')
            return render_template('signup.html')

        # Check if email is already registered
        if any(user['email'] == email for user in users.values()):
            flash('Email already registered', 'error')
            return render_template('signup.html')

        # Store user
        users[username] = {
            'email': email,
            'password': password,  # In production, hash the password
            'verified': True,
            'registered_on': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        flash('Sign up successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')


@app.route('/login/google')
def login_google():
    """Handle Google OAuth Sign-In"""
    return handle_google_login(users)

@app.route('/verify/google', methods=['POST'])
def verify_google():
    """Verify Google Sign-In email"""
    email = request.form.get('email')
    verification_code = request.form.get('verification_code')

    if email not in verification_codes:
        flash('Please start the signup process again', 'error')
        return render_template('login.html', signup=True)

    stored = verification_codes[email]
    if datetime.now() - stored['timestamp'] > timedelta(minutes=10):
        del verification_codes[email]
        flash('Code expired', 'error')
        return render_template('login.html', signup=True)

    if verification_code != stored['code']:
        flash('Invalid code', 'error')
        return render_template('login.html', signup=True, verify_email=True,
                            email=email, google_auth=True)

    # Check if user with this email already exists
    existing_user = None
    for username, user in users.items():
        if user.get('email') == email:
            existing_user = username
            break

    if existing_user:
        # Update existing user with Google auth
        users[existing_user]['google_auth'] = True
        username = existing_user
    else:
        # Create new user with Google auth
        username = f"google_user_{random.randint(1000,9999)}"
        users[username] = {
            'email': email,
            'google_auth': True,
            'verified': True,
            'registered_on': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    del verification_codes[email]

    # Log user in
    session['logged_in'] = True
    session['username'] = username
    session['is_admin'] = False
    session['registered_on'] = users[username]['registered_on']
    flash('Successfully signed in with Google!', 'success')
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Successfully logged out!', 'success')
    return redirect(url_for('login'))

@app.route('/ai-assignment-helper')
def ai_assignment_helper():
    try:
        if not session.get('logged_in'):
            flash('Please log in to access the AI Assignment Helper', 'info')
            return redirect(url_for('login'))
        return render_template('ai_assignment_helper.html')
    except Exception as e:
        app.logger.error(f"Error rendering AI Assignment Helper page: {str(e)}")
        return render_template('error.html', error="Failed to load the AI Assignment Helper page"), 500

@app.route('/submit-assignment', methods=['POST'])
def submit_assignment():
    try:
        if not session.get('logged_in'):
            return jsonify({
                'error': 'Please log in to submit assignments',
                'redirect': url_for('login')
            }), 401

        data = {}
        extracted_text = ""
        optimization_details = ""

        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and AskAIAssignment.allowed_file(file.filename):
                if not AskAIAssignment.check_file_size(file):
                    return jsonify({
                        'error': 'File size exceeds the maximum limit (10MB)'
                    }), 400

                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{file.filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                data['image_path'] = filename
                data['image_size'] = os.path.getsize(filepath)

                optimized_path = AskAIAssignment.optimize_image(filepath)
                optimization_details = f"Image optimized and saved as {os.path.basename(optimized_path)}"

                extracted_text = AskAIAssignment.ocr_image_to_text(optimized_path)
                data['extracted_text'] = extracted_text

        # Handle text input
        if 'text' in request.form and request.form['text'].strip():
            text = request.form['text']
            data['text'] = text
            extracted_text = text

        if extracted_text:
            result = AskAIAssignment.process_text_assignment(extracted_text)
            result['optimization_details'] = optimization_details
            
            # Save submission
            submission_file = AskAIAssignment.save_submission(data)
            result['submission_id'] = submission_file
            
            return jsonify(result)
        else:
            return jsonify({
                'error': 'No content provided',
                'message': 'Please provide either text or an image'
            }), 400

    except Exception as e:
        app.logger.error(f"Error processing assignment submission: {str(e)}")
        return jsonify({
            'error': 'Failed to process the submission',
            'message': str(e)
        }), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    try:
        if not session.get('logged_in'):
            return jsonify({
                'error': 'Please log in to access files'
            }), 401
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except Exception as e:
        app.logger.error(f"Error serving uploaded file: {str(e)}")
        return jsonify({
            'error': 'File not found'
        }), 404

@app.route('/api/history')
def get_submission_history():
    try:
        if not session.get('logged_in'):
            return jsonify({
                'error': 'Please log in to view submission history'
            }), 401

        submissions = []
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            if filename.startswith('submission_') and filename.endswith('.json'):
                with open(os.path.join(app.config['UPLOAD_FOLDER'], filename)) as f:
                    submission = json.load(f)
                    submissions.append(submission)
        return jsonify(submissions)
    except Exception as e:
        app.logger.error(f"Error retrieving submission history: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve submission history'
        }), 500

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error="Internal server error"), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
