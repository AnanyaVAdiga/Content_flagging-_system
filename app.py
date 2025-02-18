from flask import Flask, request, jsonify, send_from_directory
import os
from werkzeug.utils import secure_filename
from model import process_file
import logging


app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Use an absolute path for the UPLOAD_FOLDER
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        app.logger.error('No file part in the request')
        return jsonify({'error': 'No file part in the request'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        app.logger.error('No file selected for uploading')
        return jsonify({'error': 'No file selected for uploading'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        app.logger.info(f'File saved at: {file_path}')
        
        try:
            # Pass the full file path to process_file
            relevant, irrelevant, flagged = process_file(file_path)
            return jsonify({
                'relevant': [sentence[0] for sentence in relevant],
                'irrelevant': [sentence[0] for sentence in irrelevant],
                'flagged': [sentence[0] for sentence in flagged]
            })
        except Exception as e:
            app.logger.error(f'Error processing file: {str(e)}')
            return jsonify({'error': f'Error processing file: {str(e)}'}), 500
    else:
        app.logger.error('Allowed file types are txt, pdf, doc, docx')
        return jsonify({'error': 'Allowed file types are txt, pdf, doc, docx'}), 400

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(host='0.0.0.0', port=5019)