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
        # Verify required files exist
        required_files = ['test.ct', 'test.dot', 'process3.py', 'process4.py']
        missing = [f for f in required_files if not os.path.exists(f)]
        if missing:
            return jsonify({
                'error': f'Missing files: {", ".join(missing)}',
                'status': 'error'
            }), 400

        # Run process3 with timeout
        try:
            result3 = subprocess.run(
                ["python3", "process3.py", "test.ct", "test.dot"],
                capture_output=True,
                text=True,
                timeout=15  # Fail fast
            )
            if result3.returncode != 0:
                return jsonify({
                    'error': f'Feature extraction failed: {result3.stderr[:200]}',
                    'status': 'error'
                }), 500
        except subprocess.TimeoutExpired:
            return jsonify({
                'error': 'Feature extraction timed out (15s)',
                'status': 'error'
            }), 500

        # Run process4
        result4 = subprocess.run(
            ["python3", "process4.py"],
            capture_output=True,
            text=True,
            timeout=20
        )
        
        if result4.returncode != 0:
            return jsonify({
                'error': f'Prediction failed: {result4.stderr[:200]}',
                'status': 'error'
            }), 500

        return jsonify({
            'status': 'success',
            'result': result4.stdout
        })

    except Exception as e:
        return jsonify({
            'error': f'Server error: {str(e)}',
            'status': 'error'
        }), 500

















