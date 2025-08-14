from flask import Flask, request, jsonify, send_from_directory
import subprocess
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('.', filename)

@app.route('/upload-file', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return 'No file provided', 400

        file = request.files['file']
        file_type = request.form.get('type')

        if file.filename == '':
            return 'No file selected', 400

        if file_type not in ['ct', 'dot']:
            return 'Invalid file type', 400

        filename = secure_filename(f'test.{file_type}')
        file.save(filename)
        return f'File uploaded successfully as {filename}', 200

    except Exception as e:
        return f'Upload error: {str(e)}', 500

@app.route('/run-pipeline', methods=['POST'])
def run_pipeline():
    try:
        # 1. Verify required files exist
        if not os.path.exists('test.ct') or not os.path.exists('test.dot'):
            return jsonify({'error': 'Missing CT or DOT file'}), 400

        # 2. Run process3.py with the uploaded files
        result3 = subprocess.run(
            ["python3", "process3.py", "test.ct", "test.dot"],
            capture_output=True,
            text=True
        )
        
        if result3.returncode != 0:
            return jsonify({
                'error': f'Process3 failed: {result3.stderr}',
                'step3': f'Failed: {result3.stderr[:200]}'
            }), 500
            
        step3_result = "CT and DOT processing completed"

        # 3. Run process4.py
        result4 = subprocess.run(
            ["python3", "process4.py"],
            capture_output=True,
            text=True
        )
        
        if result4.returncode != 0:
            return jsonify({
                'error': f'Process4 failed: {result4.stderr}',
                'step4': f'Failed: {result4.stderr[:200]}'
            }), 500
            
        return jsonify({
            'step3': step3_result,
            'step4': "Prediction completed",
            'result': result4.stdout.strip()
        })

    except Exception as e:
        return jsonify({'error': f'Pipeline error: {str(e)}'}), 500













