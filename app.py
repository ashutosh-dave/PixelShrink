import os
from flask import Flask, render_template, request, send_file, after_this_request
from werkzeug.utils import secure_filename
from PIL import Image
import io
import zipfile

app = Flask(__name__)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max upload size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'webp', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def pixel_shrink(input_file, target_size_kb=250, quality=95, min_quality=10):
    img = Image.open(input_file)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    output = io.BytesIO()
    img.save(output, format='JPEG', quality=quality)
    output.seek(0)
    
    while len(output.getvalue()) > target_size_kb * 1024 and quality > min_quality:
        quality -= 5
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=quality)
        output.seek(0)
    
    return output

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', error='No file part')
        files = request.files.getlist('file')
        if len(files) == 1 and files[0].filename == '':
            return render_template('index.html', error='No selected file')
        
        # Get user-defined settings
        target_size = int(request.form.get('target_size', 250))
        quality = int(request.form.get('quality', 95))
        min_quality = int(request.form.get('min_quality', 10))
        
        if len(files) == 1:
            # Single file processing
            file = files[0]
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                output = pixel_shrink(file, target_size, quality, min_quality)
                
                @after_this_request
                def clear_file(response):
                    file.seek(0)
                    file.truncate()
                    return response
                
                return send_file(
                    output,
                    as_attachment=True,
                    download_name=f"pixelshrink_{filename.rsplit('.', 1)[0]}.jpg",
                    mimetype='image/jpeg'
                )
        else:
            # Bulk processing
            memory_zip = io.BytesIO()
            with zipfile.ZipFile(memory_zip, 'w') as zf:
                for file in files:
                    if file and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        output = pixel_shrink(file, target_size, quality, min_quality)
                        zf.writestr(f"{filename.rsplit('.', 1)[0]}.jpg", output.getvalue())
                        
                        # Clear the file after processing
                        file.seek(0)
                        file.truncate()
            
            memory_zip.seek(0)
            return send_file(
                memory_zip,
                as_attachment=True,
                download_name='pixelshrink_images.zip',
                mimetype='application/zip'
            )
    
    return render_template('index.html')

if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
