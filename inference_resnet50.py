import argparse
import os
from typing import Tuple

import torch
import torch.nn as nn
from torchvision import models, transforms, datasets
from PIL import Image


IMG_SIZE = 224

val_test_transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])


def load_model(weights_path: str, device: torch.device) -> nn.Module:
    """Load ResNet50 with modified final layer for binary classification.

    The training notebook replaced the final fc with nn.Linear(num_features, 2).
    """
    model = models.resnet50(pretrained=False)
    num_features = model.fc.in_features
    model.fc = nn.Linear(num_features, 2)
    state_dict = torch.load(weights_path, map_location=device)
    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()
    return model


def predict_image(model: nn.Module, image_path: str, class_names: Tuple[str, ...], device: torch.device):
    """Predict class and probability for a single image."""
    img = Image.open(image_path).convert("RGB")
    tensor = val_test_transform(img).unsqueeze(0).to(device)
    with torch.no_grad():
        outputs = model(tensor)
        probs = torch.softmax(outputs, dim=1)[0]
        conf, pred_idx = torch.max(probs, 0)
    return class_names[pred_idx.item()], conf.item(), {class_names[i]: probs[i].item() for i in range(len(class_names))}


def evaluate_directory(model: nn.Module, data_dir: str, device: torch.device):
    """Evaluate accuracy over a directory structured like ImageFolder (e.g. test set)."""
    dataset = datasets.ImageFolder(data_dir, transform=val_test_transform)
    loader = torch.utils.data.DataLoader(dataset, batch_size=32, shuffle=False)
    correct, total = 0, 0
    with torch.no_grad():
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            _, preds = torch.max(outputs, 1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)
    accuracy = correct / total if total > 0 else 0.0
    return accuracy, dataset.classes, total


def get_class_names(train_root: str):
    """Derive class names from an ImageFolder root (alphabetical)."""
    if not os.path.isdir(train_root):
        raise FileNotFoundError(f"Directory not found: {train_root}")
    classes = [d for d in os.listdir(train_root) if os.path.isdir(os.path.join(train_root, d))]
    return tuple(sorted(classes))


def main():
    parser = argparse.ArgumentParser(description="ResNet50 inference and evaluation")
    parser.add_argument("--weights", required=True, help="Path to resnet50 .pth weights file")
    parser.add_argument("--image", help="Path to a single image for prediction")
    parser.add_argument("--test_dir", help="Path to test set root (ImageFolder structure)")
    parser.add_argument("--train_dir", default="dataset_processed/train", help="Train directory to infer class order")
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu", help="Device: cuda or cpu")
    args = parser.parse_args()

    device = torch.device(args.device if args.device == "cpu" or torch.cuda.is_available() else "cpu")

    class_names = get_class_names(args.train_dir)
    model = load_model(args.weights, device)

    if args.image:
        pred_class, confidence, dist = predict_image(model, args.image, class_names, device)
        print(f"Image: {args.image}")
        print(f"Prediction: {pred_class} (confidence {confidence:.4f})")
        print("Class probabilities:")
        for k, v in dist.items():
            print(f"  {k}: {v:.4f}")

    if args.test_dir:
        acc, classes, total = evaluate_directory(model, args.test_dir, device)
        print(f"Test set evaluated: {total} images")
        print(f"Classes: {classes}")
        print(f"Accuracy: {acc:.4f}")

    if not args.image and not args.test_dir:
        print("No --image or --test_dir provided. Nothing to do.")


if __name__ == "__main__":
    main()
