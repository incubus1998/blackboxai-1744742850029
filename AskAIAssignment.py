import os
import json
from datetime import datetime, timedelta
import re
from PIL import Image, ImageOps
import pytesseract
from flask import current_app as app
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def check_file_size(file):
    """Check if the file size is within limits."""
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    return size <= MAX_FILE_SIZE

def optimize_image(image_path):
    """Optimize the image for better OCR results."""
    try:
        image = Image.open(image_path)
        
        # Convert to RGB if necessary
        if image.mode not in ('L', 'RGB'):
            image = image.convert('RGB')
        
        # Convert to grayscale
        image = ImageOps.grayscale(image)
        
        # Enhance image for better OCR
        image = ImageOps.autocontrast(image)
        image = ImageOps.equalize(image)
        
        # Resize if image is too small
        if image.width < 1000 or image.height < 1000:
            ratio = 2
            image = image.resize((image.width * ratio, image.height * ratio), Image.LANCZOS)
        
        # Save optimized image
        optimized_path = image_path.replace('.', '_optimized.')
        image.save(optimized_path, quality=95, optimize=True)
        
        logger.info(f"Successfully optimized image: {image_path}")
        return optimized_path
    except Exception as e:
        logger.error(f"Error optimizing image {image_path}: {str(e)}")
        return image_path

def ocr_image_to_text(image_path):
    """Extract text from image using OCR."""
    try:
        # Configure Tesseract parameters for better accuracy
        custom_config = r'--oem 3 --psm 6'
        
        # Perform OCR
        text = pytesseract.image_to_string(Image.open(image_path), config=custom_config)
        
        # Clean up the extracted text
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        
        logger.info(f"Successfully performed OCR on image: {image_path}")
        return text
    except Exception as e:
        logger.error(f"Error during OCR for {image_path}: {str(e)}")
        return ""

def analyze_text(text):
    """Analyze text for various metrics and patterns."""
    metrics = {
        'word_count': len(text.split()),
        'sentence_count': len(re.split(r'[.!?]+', text)),
        'character_count': len(text),
        'average_word_length': sum(len(word) for word in text.split()) / len(text.split()) if text else 0,
        'is_question': any(text.lower().startswith(q) for q in ['what', 'why', 'how', 'when', 'where', 'who', 'which']),
        'keywords': extract_keywords(text)
    }
    return metrics

def extract_keywords(text):
    """Extract important keywords from text."""
    # Simple keyword extraction (can be enhanced with NLP libraries)
    words = text.lower().split()
    stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
    keywords = [word for word in words if word not in stopwords and len(word) > 3]
    return list(set(keywords))[:10]  # Return top 10 unique keywords

def process_text_assignment(text):
    """Process and analyze the submitted text with temporal context."""
    try:
        # Clean the text
        text = text.strip()
        if not text:
            return {
                'answer': 'No text provided for analysis.',
                'summary': 'Empty submission',
                'explanation': 'Please provide some text to analyze.'
            }

        # Analyze the text
        metrics = analyze_text(text)

        # Check for temporal context keywords
        temporal_keywords = ['today', 'tomorrow', 'yesterday', 'next week', 'last week', 'next month', 'last month', 'next year', 'last year']
        temporal_found = any(kw in text.lower() for kw in temporal_keywords)

        temporal_info = ''
        if temporal_found:
            now = datetime.now()
            if 'today' in text.lower():
                temporal_info = f"Today's date is {now.strftime('%Y-%m-%d')}."
            elif 'tomorrow' in text.lower():
                tomorrow = now + timedelta(days=1)
                temporal_info = f"Tomorrow's date is {tomorrow.strftime('%Y-%m-%d')}."
            elif 'yesterday' in text.lower():
                yesterday = now - timedelta(days=1)
                temporal_info = f"Yesterday's date was {yesterday.strftime('%Y-%m-%d')}."
            elif 'next week' in text.lower():
                next_week = now + timedelta(weeks=1)
                temporal_info = f"Date one week from today is {next_week.strftime('%Y-%m-%d')}."
            elif 'last week' in text.lower():
                last_week = now - timedelta(weeks=1)
                temporal_info = f"Date one week ago was {last_week.strftime('%Y-%m-%d')}."
            elif 'next month' in text.lower():
                month = (now.month % 12) + 1
                year = now.year + (now.month // 12)
                temporal_info = f"Next month is {year}-{month:02d}."
            elif 'last month' in text.lower():
                month = (now.month - 2) % 12 + 1
                year = now.year - 1 if now.month == 1 else now.year
                temporal_info = f"Last month was {year}-{month:02d}."
            elif 'next year' in text.lower():
                temporal_info = f"Next year is {now.year + 1}."
            elif 'last year' in text.lower():
                temporal_info = f"Last year was {now.year - 1}."

        # Generate response based on text type
        if metrics['is_question']:
            answer = f"Your question is about {' '.join(metrics['keywords'][:3])}."
            if temporal_info:
                answer += f" {temporal_info}"
            summary = f"This is a question-type submission with {metrics['word_count']} words"
            explanation = "The question appears to be seeking information about relevant topics and temporal context."
        else:
            answer = f"Analysis of your text submission containing {metrics['word_count']} words."
            if temporal_info:
                answer += f" {temporal_info}"
            summary = f"Text contains {metrics['sentence_count']} sentences with an average word length of {metrics['average_word_length']:.1f} characters"
            explanation = f"Key topics identified: {', '.join(metrics['keywords'])}"

        return {
            'answer': answer,
            'summary': summary,
            'explanation': explanation,
            'metadata': metrics
        }
    except Exception as e:
        logger.error(f"Error processing text assignment: {str(e)}")
        return {
            'answer': 'Error processing submission',
            'summary': 'An error occurred',
            'explanation': 'Please try again with different text'
        }

def save_submission(data):
    """Save the submission data to a JSON file."""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        submission = {
            'timestamp': timestamp,
            'data': data,
            'metadata': {
                'submission_time': datetime.now().isoformat(),
                'file_type': data.get('image_path', '').split('.')[-1] if data.get('image_path') else 'text'
            }
        }
        
        # Ensure upload directory exists
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Save submission
        filename = f'submission_{timestamp}.json'
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        with open(filepath, 'w') as f:
            json.dump(submission, f, indent=4)
            
        logger.info(f"Successfully saved submission: {filename}")
        return filename
    except Exception as e:
        logger.error(f"Error saving submission: {str(e)}")
        return None
