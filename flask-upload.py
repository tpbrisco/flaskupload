
from flask import Flask, flash, request, redirect, url_for, send_from_directory
import flask_uploads
from werkzeug.utils import secure_filename
import os, sys, time

UPLOAD_FOLDER = '/tmp/uploads'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/upload', methods=['POST', 'GET'])
def upload_file():
    print "Method:",request.method    
    if request.method == 'POST':
        # check if POST request has file part
        if 'file' not in request.files:
            print "\'file\' not in request.files"
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            print 'No selected file'
            return redirect(request.url)
        if file and file.filename:
            # filename = secure_filename(file.filename)
            filename = secure_filename(file.filename)
            print "Saving",file
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print "Saving",os.path.join(app.config['UPLOAD_FOLDER'], filename)
            return redirect(url_for('upload_file', filename=filename))
    return '''
    <!doctype html>
    <title>Upload new file</title>
    <form action="" method=post enctype=multipart/form-data>
    <p><input type=file name=file>
          <input type=submit value="Upload">
    </form>
    <p>%s</p>
    ''' % "<br>".join(os.listdir(app.config['UPLOAD_FOLDER']))
if not os.path.isdir(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True, host='0.0.0.0', port=5010)

