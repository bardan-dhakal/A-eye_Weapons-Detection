# 🗂️ Guns and Knives YOLO Dataset

This directory contains the training dataset for weapon detection models.

## 📁 Structure

```
guns-knives-yolo_dataset/
├── corrected_dataset.yaml      # Corrected dataset configuration
├── guns-knives-yolo/           # Main dataset directory
│   ├── data.yaml              # YOLO dataset configuration
│   ├── train/                 # Training images and labels
│   │   ├── images/           # Training images
│   │   └── labels/           # Training annotations
│   ├── valid/                 # Validation images and labels
│   │   ├── images/           # Validation images
│   │   └── labels/           # Validation annotations
│   └── test/                  # Test images and labels
│       ├── images/           # Test images
│       └── labels/           # Test annotations
```

## 🎯 Dataset Information

### Classes
- **Class 0**: knife
- **Class 1**: pistol

### Statistics
- **Total Images**: ~2,000 images
- **Training Set**: ~1,400 images (70%)
- **Validation Set**: ~400 images (20%)
- **Test Set**: ~200 images (10%)

### Image Properties
- **Format**: JPG/PNG
- **Resolution**: Various (resized to 640x640 during training)
- **Annotation Format**: YOLO format (.txt)

## 📝 Dataset Configuration

### data.yaml
```yaml
# Dataset configuration file
path: /path/to/dataset  # Dataset root dir
train: train/images     # Train images (relative to 'path')
val: valid/images       # Val images (relative to 'path')
test: test/images       # Test images (optional)

# Classes
nc: 2  # Number of classes
names: ['knife', 'pistol']  # Class names
```

### corrected_dataset.yaml
This file contains corrected paths for different environments (local, Kaggle, etc.).

## 🚀 Usage

### For Training
```python
from ultralytics import YOLO

# Load dataset configuration
model = YOLO('yolov8n.pt')  # Load a pretrained model

# Train the model
results = model.train(
    data='guns-knives-yolo_dataset/data.yaml',
    epochs=100,
    imgsz=640,
    batch=16
)
```

### For Kaggle Training
```python
# Use corrected_dataset.yaml for Kaggle environment
results = model.train(
    data='guns-knives-yolo_dataset/corrected_dataset.yaml',
    epochs=100,
    imgsz=640,
    batch=16
)
```

## 📊 Dataset Quality

### Annotation Quality
- All images manually annotated
- Bounding boxes tightly fitted around objects
- Multiple objects per image supported
- Occluded objects properly labeled

### Image Diversity
- Various lighting conditions
- Different backgrounds
- Multiple angles and perspectives
- Different weapon types and models

## 🔧 Preprocessing

### Data Augmentation
Applied during training:
- Random horizontal flip
- Random brightness/contrast adjustment
- Random rotation (±15 degrees)
- Random scale (0.8-1.2x)

### Normalization
- Images normalized to [0, 1] range
- Mean: [0.485, 0.456, 0.406]
- Std: [0.229, 0.224, 0.225]

## 📈 Performance Metrics

### Validation Results
- **mAP@0.5**: 0.85+
- **mAP@0.5:0.95**: 0.65+
- **Precision**: 0.90+
- **Recall**: 0.80+

## 🚨 Important Notes

1. **Ethical Use**: This dataset is intended for security and safety applications only
2. **Privacy**: All images are properly licensed and anonymized
3. **Accuracy**: Manual verification of all annotations
4. **Updates**: Dataset may be updated with new images and corrections

## 🔗 Related Files

- [Training Scripts](../models_and_checkpoints/)
- [Model Evaluation](../runs/)
- [Backend Implementation](../backend/)

## 📄 License

This dataset is provided for research and educational purposes. Please ensure compliance with local laws and regulations when using this dataset.

---

**Dataset Version**: 1.0  
**Last Updated**: 2024  
**Maintainer**: A-eye Team
