"""
ResNet50 Model Loader for Brain MRI Classification
Adapted from gradcam_resnet/17gradcam.ipynb
"""
import torch
import torch.nn as nn
from torchvision import models
from config import Config
import os

class ResNet50Model:
    """ResNet50 model wrapper for brain tumor classification"""
    
    def __init__(self, model_path=None, device=None):
        """
        Initialize ResNet50 model
        
        Args:
            model_path: Path to trained .pth file
            device: torch.device (cuda/cpu)
        """
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_path = model_path or Config.MODEL_PATH
        self.model = None
        self.loaded = False
        
    def load_model(self):
        """Load ResNet50 architecture and trained weights"""
        if self.loaded:
            return self.model
        
        # Initialize ResNet50 architecture
        resnet50 = models.resnet50(weights=None)
        num_features = resnet50.fc.in_features
        resnet50.fc = nn.Linear(num_features, 2)  # Binary: tumor (1) vs no_tumor (0)
        resnet50 = resnet50.to(self.device)
        
        # Load trained weights
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model checkpoint not found at: {self.model_path}")
        
        checkpoint = torch.load(self.model_path, map_location=self.device)
        resnet50.load_state_dict(checkpoint)
        resnet50.eval()  # Set to evaluation mode
        
        self.model = resnet50
        self.loaded = True
        
        num_params = sum(p.numel() for p in resnet50.parameters())
        print(f"✓ ResNet50 loaded successfully ({num_params:,} parameters)")
        
        return self.model
    
    def get_target_layer(self):
        """Get the target layer for Grad-CAM (last residual block)"""
        if not self.loaded:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        return self.model.layer4[-1]
    
    def predict(self, image_tensor):
        """
        Run inference on preprocessed image tensor
        
        Args:
            image_tensor: torch.Tensor of shape (1, 3, 224, 224)
        
        Returns:
            predicted_class: int (0=no_tumor, 1=tumor)
            probabilities: dict {'tumor': float, 'no_tumor': float}
        """
        if not self.loaded:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        with torch.no_grad():
            image_tensor = image_tensor.to(self.device)
            output = self.model(image_tensor)
            probs = torch.softmax(output, dim=1)[0]
            predicted_class = output.argmax(dim=1).item()
            
        return predicted_class, {
            'no_tumor': float(probs[0]),
            'tumor': float(probs[1])
        }

# Singleton instance (load model once at startup)
_model_instance = None

def get_model():
    """Get or create singleton model instance"""
    global _model_instance
    if _model_instance is None:
        _model_instance = ResNet50Model()
        _model_instance.load_model()
    return _model_instance
