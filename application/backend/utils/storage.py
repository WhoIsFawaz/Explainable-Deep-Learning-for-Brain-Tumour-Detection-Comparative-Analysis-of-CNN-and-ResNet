"""
Storage utilities for file management (local filesystem, Azure Blob later)
"""
import os
import uuid
from pathlib import Path
from config import Config

def generate_unique_id():
    """Generate unique identifier for uploaded files"""
    return str(uuid.uuid4())

def save_uploaded_file(file, folder=None):
    """
    Save uploaded file to local storage
    
    Args:
        file: FileStorage object from Flask request
        folder: Target folder (defaults to Config.UPLOAD_FOLDER)
    
    Returns:
        file_path: Relative path to saved file
        file_id: Unique identifier
    """
    folder = folder or Config.UPLOAD_FOLDER
    os.makedirs(folder, exist_ok=True)
    
    # Generate unique ID
    file_id = generate_unique_id()
    file_ext = '.' + file.filename.rsplit('.', 1)[-1].lower()
    filename = f"{file_id}{file_ext}"
    
    # Save file
    file_path = os.path.join(folder, filename)
    file.save(file_path)
    
    return file_path, file_id

def get_absolute_path(relative_path):
    """Convert relative path to absolute path"""
    return os.path.abspath(relative_path)

def delete_file(file_path):
    """
    Delete file from storage
    
    Args:
        file_path: Path to file
    
    Returns:
        bool: True if successful
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
        return True
    except Exception as e:
        print(f"Error deleting file {file_path}: {e}")
        return False

# ==================== Azure Blob Storage (Future Migration) ====================
# When migrating to Azure, replace functions above with Azure Blob SDK calls:
#
# from azure.storage.blob import BlobServiceClient
#
# def save_to_azure_blob(file, container_name):
#     blob_service = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
#     container_client = blob_service.get_container_client(container_name)
#     blob_name = generate_unique_id() + file_ext
#     blob_client = container_client.get_blob_client(blob_name)
#     blob_client.upload_blob(file)
#     return blob_client.url
