import os
import json
from datetime import datetime
import re
from PIL import Image, ImageOps
import pytesseract
from flask import current_app as app

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def optimize_image(image_path):
    try:
        image = Image.open(image_path)
        image = ImageOps.grayscale(image)
        image = image.resize((image.width * 2, image.height * 2), Image.ANTIALIAS)
        optimized_path = image_path.replace('.', '_optimized.')
        image.save(optimized_path)
        return optimized_path
    except Exception as e:
        app.logger.error(f"Error optimizing image: {str(e)}")
        return image_path

def ocr_image_to_text(image_path):
    try:
        text = pytesseract.image_to_string(Image.open(image_path))
        return text.strip()
    except Exception as e:
        app.logger.error(f"Error during OCR: {str(e)}")
        return ""

def process_text_assignment(text):
    text = re.sub(r'\s+', ' ', text.strip())
    word_count = len(text.split())
    sentence_count = len(re.split(r'[.!?]+', text))
    is_question = any(text.lower().startswith(q) for q in ['what', 'why', 'how', 'when', 'where', 'who', 'which'])
    if is_question:
        answer = f"Here's the answer to your question about {text.split()[1:4]}..."
        summary = f"Your question is about {text.split()[1:4]}"
        explanation = "Based on the analysis, this question requires..."
    else:
        answer = "Here's an analysis of your text submission..."
        summary = f"Text contains {word_count} words and {sentence_count} sentences"
        explanation = "The submission appears to be a statement or description..."
    return {
        'answer': answer,
        'summary': summary,
        'explanation': explanation,
        'metadata': {
            'word_count': word_count,
            'sentence_count': sentence_count,
            'is_question': is_question
        }
    }

def save_submission(data):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    submission = {
        'timestamp': timestamp,
        'data': data
    }
    filename = f'submission_{timestamp}.json'
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    with open(filepath, 'w') as f:
        json.dump(submission, f, indent=4)
    return filename
