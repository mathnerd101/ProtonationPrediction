from flask import Flask, request, jsonify, send_from_directory
import subprocess
import os
import pandas as pd  # Add this import
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
        # Verify files exist with absolute paths
        ct_path = os.path.abspath('test.ct')
        dot_path = os.path.abspath('test.dot')
        
        if not os.path.exists(ct_path) or not os.path.exists(dot_path):
            return jsonify({
                'error': 'Missing input files',
                'details': {
                    'ct_exists': os.path.exists(ct_path),
                    'dot_exists': os.path.exists(dot_path)
                }
            }), 400

        # Run process3.py
        process3_path = os.path.abspath('process3.py')
        result3 = subprocess.run(
            ["python3", process3_path, ct_path, dot_path],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result3.returncode != 0:
            return jsonify({
                'error': 'Feature extraction failed',
                'stderr': result3.stderr[:500],
                'stdout': result3.stdout[:500]
            }), 500

        # Run process4.py
        process4_path = os.path.abspath('process4.py')
        result4 = subprocess.run(
            ["python3", process4_path],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        return jsonify({
            'step3': 'Feature extraction completed',
            'step4': 'Prediction completed',
            'result': result4.stdout.strip(),
            'prediction_stderr': result4.stderr[:500] if result4.stderr else None
        })

    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Pipeline timed out'}), 500
    except Exception as e:
        return jsonify({
            'error': 'Unexpected pipeline error',
            'details': str(e)
        }), 500

@app.route("/get_predictions")
def get_predictions():
    path = os.path.join(os.path.dirname(__file__), "predictions.csv")
    if not os.path.exists(path):
        return jsonify({"error": "No predictions found"}), 404

    try:
        df = pd.read_csv(path)
        return df.to_json(orient="records")
    except Exception as e:
        return jsonify({"error": f"Error reading predictions: {str(e)}"}), 500

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)
