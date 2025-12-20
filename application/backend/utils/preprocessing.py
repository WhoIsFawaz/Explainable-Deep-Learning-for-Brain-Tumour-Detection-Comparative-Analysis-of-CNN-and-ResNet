"""
Image preprocessing utilities for brain MRI classification
"""
import torch
from torchvision import transforms
from PIL import Image
from config import Config

def get_preprocessing_transform():
    """
    Get ResNet50 preprocessing pipeline (ImageNet normalization)
    
    Returns:
        torchvision.transforms.Compose object
    """
    return transforms.Compose([
        transforms.Resize((Config.IMG_SIZE, Config.IMG_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])  # ImageNet stats
    ])

def preprocess_image(image_path):
    """
    Load and preprocess image for model inference
    
    Args:
        image_path: Path to image file (str or Path object)
    
    Returns:
        image_tensor: torch.Tensor of shape (1, 3, 224, 224)
        original_image: PIL.Image (for reference)
    """
    transform = get_preprocessing_transform()
    
    # Load image
    img = Image.open(image_path).convert('RGB')
    
    # Apply preprocessing
    img_tensor = transform(img).unsqueeze(0)  # Add batch dimension
    
    return img_tensor, img

def validate_image_file(file):
    """
    Validate uploaded image file
    
    Args:
        file: FileStorage object from Flask request
    
    Returns:
        bool: True if valid
    
    Raises:
        ValueError: If file is invalid
    """
    if not file:
        raise ValueError("No file provided")
    
    if file.filename == '':
        raise ValueError("Empty filename")
    
    # Check file extension
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
    file_ext = '.' + file.filename.rsplit('.', 1)[-1].lower()
    
    if file_ext not in allowed_extensions:
        raise ValueError(f"Invalid file type. Allowed: {', '.join(allowed_extensions)}")
    
    # Check file size (max 10MB)
    file.seek(0, 2)  # Seek to end
    file_size = file.tell()
    file.seek(0)  # Reset position
    
    max_size = 10 * 1024 * 1024  # 10MB
    if file_size > max_size:
        raise ValueError(f"File too large. Maximum size: {max_size / (1024*1024)}MB")
    
    return True
