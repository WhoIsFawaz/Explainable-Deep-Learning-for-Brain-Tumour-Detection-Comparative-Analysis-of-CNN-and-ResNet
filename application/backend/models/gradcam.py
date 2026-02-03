"""
Grad-CAM Implementation for Explainable AI
Adapted from gradcam_resnet/17gradcam.ipynb
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import cv2
from PIL import Image

class GradCAM:
    """
    Gradient-weighted Class Activation Mapping (Grad-CAM)
    Highlights important regions in the image that influence the model's prediction.
    """
    def __init__(self, model, target_layer):
        """
        Initialize Grad-CAM
        
        Args:
            model: PyTorch model
            target_layer: Layer to compute gradients from (e.g., model.layer4[-1])
        """
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        
        # Register hooks to capture gradients and activations
        self.target_layer.register_forward_hook(self.save_activation)
        self.target_layer.register_backward_hook(self.save_gradient)
    
    def save_activation(self, module, input, output):
        """Hook to save forward pass activations"""
        self.activations = output.detach()
    
    def save_gradient(self, module, grad_input, grad_output):
        """Hook to save backward pass gradients"""
        self.gradients = grad_output[0].detach()
    
    def generate_heatmap(self, input_image, class_idx=None):
        """
        Generate Grad-CAM heatmap for the predicted or specified class
        
        Args:
            input_image: torch.Tensor of shape (1, 3, 224, 224)
            class_idx: Target class index (optional, uses predicted class if None)
        
        Returns:
            heatmap: numpy array of shape (H, W) with values in [0, 1]
            class_idx: Predicted or specified class index
        """
        # Forward pass to get prediction
        output = self.model(input_image)
        
        # Use predicted class if not specified
        if class_idx is None:
            class_idx = output.argmax(dim=1).item()
        
        # Backward pass to get gradients
        self.model.zero_grad()
        class_score = output[:, class_idx]
        class_score.backward()
        
        # Weight activations by average gradient (global average pooling)
        pooled_gradients = torch.mean(self.gradients, dim=[0, 2, 3])
        
        # Apply weights to activations
        for i in range(self.activations.shape[1]):
            self.activations[:, i, :, :] *= pooled_gradients[i]
        
        # Average across channels to get final heatmap
        heatmap = torch.mean(self.activations, dim=1).squeeze()
        
        # Apply ReLU to focus on positive influences
        heatmap = F.relu(heatmap)
        
        # Normalize to [0, 1] range
        heatmap /= torch.max(heatmap) if torch.max(heatmap) > 0 else 1.0
        
        return heatmap.cpu().numpy(), class_idx

def create_gradcam_overlay(original_image_path, heatmap, img_size=224, alpha=0.4):
    """
    Create Grad-CAM overlay visualization
    
    Args:
        original_image_path: Path to original image file
        heatmap: numpy array from GradCAM.generate_heatmap()
        img_size: Target image size (default 224)
        alpha: Overlay transparency (default 0.4)
    
    Returns:
        original: RGB image array
        heatmap_colored: Colored heatmap array
        overlay: Blended overlay array
    """
    # Load original image
    img = cv2.imread(str(original_image_path))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (img_size, img_size))
    
    # Resize heatmap to image size
    heatmap_resized = cv2.resize(heatmap, (img_size, img_size))
    
    # Convert heatmap to colored version (jet colormap)
    heatmap_colored = np.uint8(255 * heatmap_resized)
    heatmap_colored = cv2.applyColorMap(heatmap_colored, cv2.COLORMAP_JET)
    heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)
    
    # Blend original image with heatmap
    overlay = cv2.addWeighted(img, 1-alpha, heatmap_colored, alpha, 0)
    
    return img, heatmap_colored, overlay

def save_gradcam_images(output_dir, image_id, original, heatmap_colored, overlay):
    """
    Save Grad-CAM visualization images to storage (Azure Blob or local)
    
    Args:
        output_dir: Directory to save images (used for local storage only)
        image_id: Unique identifier for this prediction
        original: Original image array (RGB format)
        heatmap_colored: Colored heatmap array (RGB format)
        overlay: Overlay array (RGB format)
    
    Returns:
        dict with paths/URLs to saved files
    """
    from utils.storage import save_gradcam_to_storage, USE_AZURE_STORAGE
    import os
    
    paths = {}
    
    if USE_AZURE_STORAGE:
        # Save to Azure Blob Storage - convert RGB to BGR for cv2
        paths['original'] = save_gradcam_to_storage(
            cv2.cvtColor(original, cv2.COLOR_RGB2BGR),
            f"{image_id}_original.png"
        )
        paths['heatmap'] = save_gradcam_to_storage(
            cv2.cvtColor(heatmap_colored, cv2.COLOR_RGB2BGR),
            f"{image_id}_heatmap.png"
        )
        paths['overlay'] = save_gradcam_to_storage(
            cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR),
            f"{image_id}_overlay.png"
        )
    else:
        # Save to local filesystem
        os.makedirs(output_dir, exist_ok=True)
        
        # Save original
        original_path = os.path.join(output_dir, f"{image_id}_original.png")
        cv2.imwrite(original_path, cv2.cvtColor(original, cv2.COLOR_RGB2BGR))
        paths['original'] = original_path
        
        # Save heatmap
        heatmap_path = os.path.join(output_dir, f"{image_id}_heatmap.png")
        cv2.imwrite(heatmap_path, cv2.cvtColor(heatmap_colored, cv2.COLOR_RGB2BGR))
        paths['heatmap'] = heatmap_path
        
        # Save overlay
        overlay_path = os.path.join(output_dir, f"{image_id}_overlay.png")
        cv2.imwrite(overlay_path, cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR))
        paths['overlay'] = overlay_path
    
    return paths
