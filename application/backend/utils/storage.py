"""
Storage utilities for file management (local filesystem + Azure Blob Storage)
"""
import os
import uuid
from pathlib import Path
from config import Config

# Check if Azure Blob Storage is configured
AZURE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING', '')
AZURE_CONTAINER_UPLOADS = os.getenv('AZURE_STORAGE_CONTAINER_UPLOADS', 'uploads')
AZURE_CONTAINER_GRADCAM = os.getenv('AZURE_STORAGE_CONTAINER_GRADCAM', 'gradcam-outputs')
USE_AZURE_STORAGE = bool(AZURE_CONNECTION_STRING)

# Only import Azure SDK if we're using Azure
if USE_AZURE_STORAGE:
    from azure.storage.blob import BlobServiceClient, ContentSettings

def generate_unique_id():
    """Generate unique identifier for uploaded files"""
    return str(uuid.uuid4())

def save_uploaded_file(file, folder=None):
    """
    Save uploaded file to storage (Azure Blob or local filesystem)
    
    Args:
        file: FileStorage object from Flask request
        folder: Target folder (defaults to Config.UPLOAD_FOLDER)
    
    Returns:
        file_path: URL (Azure) or relative path (local)
        file_id: Unique identifier
    """
    # Generate unique ID
    file_id = generate_unique_id()
    file_ext = '.' + file.filename.rsplit('.', 1)[-1].lower()
    filename = f"{file_id}{file_ext}"
    
    if USE_AZURE_STORAGE:
        # Save to Azure Blob Storage
        blob_service = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
        container_client = blob_service.get_container_client(AZURE_CONTAINER_UPLOADS)
        blob_client = container_client.get_blob_client(filename)
        
        file.seek(0)  # Reset file pointer
        blob_client.upload_blob(
            file.read(),
            content_settings=ContentSettings(content_type='image/png'),
            overwrite=True
        )
        
        # Return the blob URL
        file_path = blob_client.url
        return file_path, file_id
    else:
        # Save to local filesystem (development)
        folder = folder or Config.UPLOAD_FOLDER
        os.makedirs(folder, exist_ok=True)
        
        file_path = os.path.join(folder, filename)
        file.save(file_path)
        
        return file_path, file_id

def save_gradcam_to_storage(image_array, filename):
    """
    Save Grad-CAM image to storage (Azure Blob or local)
    
    Args:
        image_array: numpy array (BGR format from cv2)
        filename: filename to save as
    
    Returns:
        str: URL (Azure) or relative path (local)
    """
    import cv2
    import numpy as np
    
    if USE_AZURE_STORAGE:
        # Encode image to bytes
        _, buffer = cv2.imencode('.png', image_array)
        image_bytes = buffer.tobytes()
        
        # Upload to Azure Blob Storage
        blob_service = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
        container_client = blob_service.get_container_client(AZURE_CONTAINER_GRADCAM)
        blob_client = container_client.get_blob_client(filename)
        
        blob_client.upload_blob(
            image_bytes,
            content_settings=ContentSettings(content_type='image/png'),
            overwrite=True
        )
        
        return blob_client.url
    else:
        # Save to local filesystem
        folder = Config.GRADCAM_FOLDER
        os.makedirs(folder, exist_ok=True)
        
        file_path = os.path.join(folder, filename)
        cv2.imwrite(file_path, image_array)
        
        return file_path

def download_blob_to_temp(blob_url):
    """
    Download Azure Blob to temporary file
    
    Args:
        blob_url: Full URL to Azure Blob
    
    Returns:
        str: Path to temporary file
    """
    import tempfile
    from azure.storage.blob import BlobServiceClient
    
    # Extract blob name and container from URL
    # URL format: https://account.blob.core.windows.net/container/blobname
    parts = blob_url.split('/')
    container_name = parts[-2]
    blob_name = parts[-1]
    
    # Download blob
    blob_service = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
    blob_client = blob_service.get_blob_client(container=container_name, blob=blob_name)
    
    # Create temp file
    suffix = os.path.splitext(blob_name)[1]
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    
    with open(temp_file.name, 'wb') as f:
        f.write(blob_client.download_blob().readall())
    
    return temp_file.name

def get_absolute_path(path_or_url):
    """
    Get absolute path for local files, or download Azure blob to temp file
    
    Args:
        path_or_url: Local path or Azure Blob URL
    
    Returns:
        str: Absolute path to file (temp file if Azure URL)
    """
    if USE_AZURE_STORAGE and path_or_url.startswith('http'):
        # Download blob to temp file for processing
        return download_blob_to_temp(path_or_url)
    return os.path.abspath(path_or_url)

def delete_file(file_path):
    """
    Delete file from storage
    
    Args:
        file_path: Path or URL to file
    
    Returns:
        bool: True if successful
    """
    try:
        if USE_AZURE_STORAGE and file_path.startswith('http'):
            # Delete from Azure Blob Storage
            # Extract blob name from URL
            blob_name = file_path.split('/')[-1]
            container_name = AZURE_CONTAINER_UPLOADS if '/uploads/' in file_path else AZURE_CONTAINER_GRADCAM
            
            blob_service = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
            container_client = blob_service.get_container_client(container_name)
            blob_client = container_client.get_blob_client(blob_name)
            blob_client.delete_blob()
        else:
            # Delete from local filesystem
            if os.path.exists(file_path):
                os.remove(file_path)
        return True
    except Exception as e:
        print(f"Error deleting file {file_path}: {e}")
        return False
