import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

def allowed_file(filename):
    if not filename or '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in current_app.config.get('ALLOWED_EXTENSIONS', {'png', 'jpg', 'jpeg', 'webp', 'gif'})

def save_uploaded_file(file_storage, subfolder='issues'):
    """
    Saves an uploaded file to the specified subfolder within static/uploads.
    Returns the relative path for serving the file, e.g. 'uploads/issues/xyz.jpg'
    """
    if not file_storage or file_storage.filename == '':
        return None
        
    if not allowed_file(file_storage.filename):
        raise ValueError('Invalid file extension. Allowed formats: PNG, JPG, JPEG, WEBP, GIF.')
        
    original_name = secure_filename(file_storage.filename)
    extension = original_name.rsplit('.', 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex[:12]}_{original_name}"
    
    target_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
    os.makedirs(target_dir, exist_ok=True)
    
    file_path = os.path.join(target_dir, unique_filename)
    file_storage.save(file_path)
    
    # Return relative URL from static root
    return f"uploads/{subfolder}/{unique_filename}"
