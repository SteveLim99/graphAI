import os
from flask import Flask, flash, request, redirect, url_for

app = Flask(__name__)
UPLOAD_FOLDER = os.getcwd() + "/uploads"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/test')
def test():
    return "Hello React"


@app.route('/fileUpload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "Missing File"
        file = request.files['file']
        if file.filename == '':
            return "No Selected File"
        if file and validateFileExtension(file.filename):
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
            return "File Uploaded"


def validateFileExtension(fileExtension):
    return '.' in fileExtension and fileExtension.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
