@app.route('/upload-file', methods=['POST'])
def upload_file():
    try:
        # Check if the post request has the file part
        if 'file' not in request.files:
            return 'No file provided', 400

        file = request.files['file']
        file_type = request.form.get('type')

        # If the user does not select a file, the browser submits an
        # empty file without a filename
        if file.filename == '':
            return 'No file selected', 400

        if file and file_type in ['ct', 'dot']:
            filename = secure_filename(f'test.{file_type}')
            file.save(filename)
            return f'File uploaded successfully as {filename}', 200
        else:
            return 'Invalid file type', 400

    except Exception as e:
        return f'Upload error: {str(e)}', 500
