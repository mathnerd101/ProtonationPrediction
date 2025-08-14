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
        required_files = ['process3.py', 'process4.py']
        for f in required_files:
            if not os.path.exists(f):
                return jsonify({'error': f'Missing required file: {f}'}), 400

        # 2. Run process3.py with enhanced error handling
        try:
            result3 = subprocess.run(
                ["python3", os.path.abspath("process3.py")],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result3.returncode != 0:
                return jsonify({
                    'error': f'Process3 failed: {result3.stderr}',
                    'step3': f'Failed: {result3.stderr[:200]}'
                }), 500
                
            step3_result = "CSV processing completed successfully"
        except subprocess.TimeoutExpired:
            return jsonify({'error': 'Process3 timed out after 60 seconds'}), 500

        # 3. Run process4.py with enhanced error handling
        try:
            result4 = subprocess.run(
                ["python3", os.path.abspath("process4.py")],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result4.returncode != 0:
                return jsonify({
                    'error': f'Process4 failed: {result4.stderr}',
                    'step4': f'Failed: {result4.stderr[:200]}'
                }), 500
                
            step4_result = "Model prediction completed successfully"
            final_result = result4.stdout.strip() or "No output from process4"
        except subprocess.TimeoutExpired:
            return jsonify({'error': 'Process4 timed out after 60 seconds'}), 500

        # 4. Successful response
        return jsonify({
            'step3': step3_result,
            'step4': step4_result,
            'result': final_result
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Unexpected pipeline error: {str(e)}'}), 500












