import os
import uuid
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {
    'pdf': ['pdf'],
    'image': ['png', 'jpg', 'jpeg', 'gif'],
    'video': ['mp4', 'avi', 'mov'],
    'document': ['doc', 'docx', 'txt']
}

def allowed_file(filename, allowed_types):
    """Check if file extension is allowed"""
    if not filename:
        return False
    
    extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    return extension in allowed_types

def save_uploaded_file(file, upload_folder):
    """Save uploaded file with unique name"""
    if file and file.filename:
        # Generate unique filename
        file_extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        unique_filename = f"{uuid.uuid4().hex[:12]}.{file_extension}"
        
        # Ensure upload folder exists
        os.makedirs(upload_folder, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        return unique_filename
    return None

def get_file_size(file_path):
    """Get file size in bytes"""
    try:
        return os.path.getsize(file_path)
    except OSError:
        return 0

def delete_file(file_path):
    """Delete file if it exists"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    except OSError:
        pass
    return False

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    size_index = 0
    
    while size_bytes >= 1024 and size_index < len(size_names) - 1:
        size_bytes /= 1024.0
        size_index += 1
    
    return f"{size_bytes:.1f} {size_names[size_index]}"
