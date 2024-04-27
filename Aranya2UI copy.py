from flask import Flask, render_template, request
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'wmv'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    print('Hello, Flask!') 
    return render_template('index.html')

@app.route('/demo')
def demo():
    print('DEMO, Flask!') 
    file_name="static/img/gallery-7.jpg"
    # names = ["Python", "PHP", "JS", "Go"]
    # print(names)
    return render_template('product.html', file_name=file_name)
    # return render_template('product.html')


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    # if request.method == 'POST':
    print('0. START UPLOADING ...') 
    if 'file' not in request.files:
        print('1. FILE COULD NOT BE FOUND ???') 
        return 'No file part in the request', 400

    if 'file' in request.files:
        f = request.files['file']
        print('1. FILE TO BE UPLOADED...', f) 
        if f and allowed_file(f.filename):
            print('2. ALLOWED file type & UPLOADING ...') 
            basepath = os.path.dirname(__file__)
            filepath = os.path.join(basepath,'uploads',f.filename)
            print("upload folder is ", filepath)
            # f.save(filepath)

            # Here you should save the file
            path_to_save_file = "static/uploaded/TEST.jpg"
            f.save(path_to_save_file)
            # filename = secure_filename(f.filename)
            print('File SAVED successfully', path_to_save_file)

            file_name="static/img/YOLO_result.jpg"
            return render_template('product.html', file_name=file_name)
        else:
            return 'File upload failed - WRONG File Type'

if __name__ == '__main__':
    app.run(debug=True)
