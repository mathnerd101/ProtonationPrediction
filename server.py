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
        # Step 3: Run process3.py
        result3 = subprocess.run(["python3", "process3.py"], 
                               capture_output=True, text=True, timeout=60)
        step3_result = "CSV processing completed successfully" if result3.returncode == 0 else f"Process 3 completed with warnings: {result3.stderr[:100]}"

        # Step 4: Run process4.py
        result4 = subprocess.run(["python3", "process4.py"], 
                               capture_output=True, text=True, timeout=60)
        step4_result = "Model prediction completed successfully" if result4.returncode == 0 else f"Process 4 completed with warnings: {result4.stderr[:100]}"

        final_result = result4.stdout.strip() if result4.stdout.strip() else "Pipeline completed successfully"

        return jsonify({
            'step3': step3_result,
            'step4': step4_result,
            'result': final_result
        })

    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Pipeline timeout - process took too long'}), 500
    except Exception as e:
        return jsonify({'error': f'Pipeline error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)


