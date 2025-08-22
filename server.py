from flask import Flask, request, jsonify, send_from_directory
import subprocess
import os
import tempfile
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
        
        # Validate file extension
        expected_extension = f'.{file_type}'
        if not file.filename.lower().endswith(expected_extension):
            return f'Invalid file extension. Expected {expected_extension}', 400
        
        # Save as test.ct or test.dot
        filename = f'test.{file_type}'
        file.save(filename)
        
        # Verify file was saved and has content
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            return f'File uploaded successfully as {filename}', 200
        else:
            return 'File upload failed - file is empty or not saved', 500
            
    except Exception as e:
        return f'Upload error: {str(e)}', 500

@app.route('/run-pipeline', methods=['POST'])
def run_pipeline():
    try:
        # Check if required files exist
        ct_file = 'test.ct'
        dot_file = 'test.dot'
        
        if not os.path.exists(ct_file):
            return jsonify({'error': 'CT file not found. Please upload a .ct file first.'}), 400
        
        if not os.path.exists(dot_file):
            return jsonify({'error': 'DOT file not found. Please upload a .dot file first.'}), 400
        
        try:
            # Step 3: Run process3.py with the uploaded files
            print("Running process3.py...")
            result3 = subprocess.run(
                ["python3", "process3.py", ct_file, dot_file], 
                capture_output=True, text=True, timeout=120
            )
            
            if result3.returncode == 0:
                step3_result = "Feature extraction completed successfully"
                print("Process 3 completed successfully")
                print("STDOUT:", result3.stdout)
            else:
                step3_result = f"Feature extraction completed with warnings: {result3.stderr[:200]}"
                print("Process 3 had warnings:", result3.stderr)
            
            # Step 4: Run process4.py for model prediction
            print("Running process4.py...")
            result4 = subprocess.run(
                ["python3", "process4.py"], 
                capture_output=True, text=True, timeout=120
            )
            
            if result4.returncode == 0:
                step4_result = "Model prediction completed successfully"
                print("Process 4 completed successfully")
                print("STDOUT:", result4.stdout)
            else:
                step4_result = f"Model prediction completed with warnings: {result4.stderr[:200]}"
                print("Process 4 had warnings:", result4.stderr)
            
            # Get final result from process4 output
            final_result = result4.stdout.strip() if result4.stdout.strip() else "Pipeline completed - check predictions.csv for results"
            
            # Check if prediction file was created
            if os.path.exists('predictions.csv'):
                with open('predictions.csv', 'r') as f:
                    lines = f.readlines()
                    if len(lines) > 1:  # Header + at least one data row
                        final_result += f"\n\nPredictions file created with {len(lines)-1} predictions."
            
            return jsonify({
                'step3': step3_result,
                'step4': step4_result,
                'result': final_result
            })
            
        except subprocess.TimeoutExpired:
            return jsonify({'error': 'Pipeline timeout - process took too long (>2 minutes)'}), 500
        except Exception as e:
            return jsonify({'error': f'Pipeline processing error: {str(e)}'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Pipeline error: {str(e)}'}), 500

@app.route('/download-predictions')
def download_predictions():
    """Allow users to download the predictions CSV file"""
    try:
        if os.path.exists('predictions.csv'):
            return send_from_directory('.', 'predictions.csv', as_attachment=True)
        else:
            return 'No predictions file available', 404
    except Exception as e:
        return f'Download error: {str(e)}', 500

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('models', exist_ok=True)
    
    print("Starting HPred-RNA server...")
    print("Make sure you have:")
    print("1. AutoGluon installed: pip install autogluon")
    print("2. Models directory with trained models")
    print("3. Upload .ct and .dot files before running pipeline")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
