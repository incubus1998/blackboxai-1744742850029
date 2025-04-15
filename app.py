from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import json
from datetime import datetime
import AskAIAssignment

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'uploads'
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    try:
        return render_template('index.html')
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

@app.route('/contact')
def contact():
    try:
        return render_template('contact.html')
    except Exception as e:
        app.logger.error(f"Error rendering contact page: {str(e)}")
        return render_template('error.html', error="Failed to load the page"), 500

@app.route('/ai-assignment-helper')
def ai_assignment_helper():
    try:
        return render_template('ai_assignment_helper.html')
    except Exception as e:
        app.logger.error(f"Error rendering AI Assignment Helper page: {str(e)}")
        return render_template('error.html', error="Failed to load the AI Assignment Helper page"), 500

@app.route('/submit-assignment', methods=['POST'])
def submit_assignment():
    try:
        data = {}
        extracted_text = ""
        optimization_details = ""

        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file and AskAIAssignment.allowed_file(file.filename):
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
            extracted_text = extracted_text.lower()
            result = AskAIAssignment.process_text_assignment(extracted_text)
        else:
            result = {
                'answer': 'Please provide text or an image to analyze.',
                'summary': 'No input detected',
                'explanation': 'The system requires either text input or an image upload to provide analysis.'
            }

        result['optimization_details'] = optimization_details

        submission_file = AskAIAssignment.save_submission(data)
        result['submission_id'] = submission_file

        return jsonify(result)

    except Exception as e:
        app.logger.error(f"Error processing assignment submission: {str(e)}")
        return jsonify({
            'error': 'Failed to process the submission',
            'message': str(e)
        }), 500

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except Exception as e:
        app.logger.error(f"Error serving uploaded file: {str(e)}")
        return jsonify({
            'error': 'File not found'
        }), 404

@app.route('/api/history')
def get_submission_history():
    try:
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

from flask import request, redirect, url_for, flash

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)

@app.route('/login/google')
def login_google():
    # Placeholder for Google OAuth login redirect
    # In a real app, redirect to Google's OAuth 2.0 authorization endpoint
    return "Redirecting to Google OAuth login (placeholder)"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Placeholder authentication logic
        if username == 'admin' and password == 'password':
            # In real app, set session or token here
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
            return redirect(url_for('login'))
    return render_template('login.html')
