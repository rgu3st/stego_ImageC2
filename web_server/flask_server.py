import os
from flask import Flask, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration for file uploads
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
NUM_FILES_UPLOADED = 0

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    global NUM_FILES_UPLOADED
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        # If user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            tmp = filename.split(".")
            filename = f"{tmp[0]}_{NUM_FILES_UPLOADED}.{tmp[-1]}"
            print(f"Saving file: {filename}")
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            NUM_FILES_UPLOADED += 1
            return redirect(url_for('uploaded_file', filename=filename))
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('index.html', files=files)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return redirect("/")
    # return redirect(url_for('static', filename=os.path.join(UPLOAD_FOLDER, filename)))

if __name__ == '__main__':
    app.run(debug=True)
