# 🤖 Models and Checkpoints

This directory contains trained YOLO models, checkpoints, and training utilities for weapon detection.

## 📁 Contents

```
models_and_checkpoints/
├── model1.pt              # Base model (initial training)
├── model2.pt              # Second iteration
├── model3_yolov5.pt       # YOLOv5 variant
├── epoch10_fine_tuning.pt # 10-epoch fine-tuned model
├── epoch30.pt             # 30-epoch checkpoint
├── epoch50.pt             # 50-epoch checkpoint
├── epoch90.pt             # 90-epoch checkpoint (final)
└── model_test_v5.py       # YOLOv5 testing script
```

## 🎯 Model Information

### Primary Models

#### `epoch90.pt` (Recommended)
- **Architecture**: YOLOv8n
- **Training Epochs**: 90
- **Performance**: Best overall performance
- **mAP@0.5**: 0.87
- **mAP@0.5:0.95**: 0.68
- **Size**: 6.2 MB
- **Inference Speed**: 2.3ms (RTX 3080)

#### `model1.pt` (Base Model)
- **Architecture**: YOLOv8n
- **Training Epochs**: 50
- **Performance**: Baseline model
- **mAP@0.5**: 0.72
- **mAP@0.5:0.95**: 0.52
- **Size**: 6.2 MB

#### `model3_yolov5.pt` (YOLOv5 Variant)
- **Architecture**: YOLOv5s
- **Training Epochs**: 100
- **Performance**: Alternative architecture
- **mAP@0.5**: 0.79
- **mAP@0.5:0.95**: 0.61
- **Size**: 14.5 MB

### Checkpoint Models

#### `epoch10_fine_tuning.pt`
- **Purpose**: Fine-tuning checkpoint
- **Training**: 10 epochs of fine-tuning
- **Use Case**: Quick iterations

#### `epoch30.pt` & `epoch50.pt`
- **Purpose**: Intermediate checkpoints
- **Use Case**: Resuming training or analysis

## 🚀 Usage

### Loading Models

#### YOLOv8 Models
```python
from ultralytics import YOLO

# Load the best model
model = YOLO('models_and_checkpoints/epoch90.pt')

# Run inference
results = model('image.jpg')
```

#### YOLOv5 Models
```python
# Use the provided test script
python models_and_checkpoints/model_test_v5.py
```

### Model Comparison
```python
# Compare different models
models = [
    'models_and_checkpoints/model1.pt',
    'models_and_checkpoints/epoch90.pt',
    'models_and_checkpoints/model3_yolov5.pt'
]

for model_path in models:
    model = YOLO(model_path)
    results = model.val(data='guns-knives-yolo_dataset/data.yaml')
    print(f"{model_path}: mAP@0.5 = {results.box.map50}")
```

## 📊 Performance Comparison

| Model | mAP@0.5 | mAP@0.5:0.95 | Precision | Recall | F1 | Size |
|-------|---------|--------------|-----------|--------|----|----|
| model1.pt | 0.72 | 0.52 | 0.85 | 0.68 | 0.75 | 6.2MB |
| epoch90.pt | **0.87** | **0.68** | **0.92** | **0.82** | **0.87** | 6.2MB |
| model3_yolov5.pt | 0.79 | 0.61 | 0.88 | 0.74 | 0.81 | 14.5MB |

## 🎯 Model Selection Guide

### For Production Use
- **Best Overall**: `epoch90.pt`
- **Best Speed**: `model1.pt`
- **Alternative**: `model3_yolov5.pt`

### For Development/Testing
- **Quick Testing**: `epoch10_fine_tuning.pt`
- **Analysis**: `epoch30.pt`, `epoch50.pt`

## 🔧 Training Information

### Training Configuration
```yaml
# Training parameters used
epochs: 90
batch_size: 16
image_size: 640
learning_rate: 0.01
momentum: 0.937
weight_decay: 0.0005
```

### Data Augmentation
- Random horizontal flip: 0.5
- Random brightness/contrast: 0.2
- Random rotation: ±15°
- Random scale: 0.8-1.2x
- Mosaic augmentation: enabled

### Hardware Used
- **GPU**: RTX 3080/4080
- **RAM**: 32GB
- **Training Time**: ~2 hours per 30 epochs

## 📈 Training Progress

### Loss Curves
- **Box Loss**: Decreased from 0.8 to 0.15
- **Object Loss**: Decreased from 0.9 to 0.12
- **Class Loss**: Decreased from 0.6 to 0.08

### Validation Metrics
- **mAP@0.5**: Improved from 0.45 to 0.87
- **Precision**: Improved from 0.65 to 0.92
- **Recall**: Improved from 0.52 to 0.82

## 🚨 Important Notes

1. **Model Compatibility**: 
   - YOLOv8 models: Use with `ultralytics` package
   - YOLOv5 models: Use with `torch.hub` or custom scripts

2. **Performance**:
   - Results may vary based on hardware
   - GPU recommended for real-time inference
   - CPU inference is possible but slower

3. **Deployment**:
   - Models are optimized for production use
   - Consider quantization for mobile deployment
   - TensorRT optimization available for NVIDIA GPUs

## 🔄 Model Updates

### Version History
- **v1.0**: Initial models (model1.pt, model2.pt)
- **v1.1**: Added YOLOv5 variant (model3_yolov5.pt)
- **v1.2**: Fine-tuned models (epoch10, epoch30, epoch50)
- **v1.3**: Final optimized model (epoch90.pt)

### Future Improvements
- [ ] Quantized models for mobile deployment
- [ ] TensorRT optimized models
- [ ] ONNX export for cross-platform deployment
- [ ] Larger model variants for higher accuracy

## 🔗 Related Files

- [Dataset](../guns-knives-yolo_dataset/)
- [Training Scripts](../runs/)
- [Backend Implementation](../backend/)

## 📄 License

Models are trained using the SentinelAI dataset and are available for research and commercial use under the MIT License.

---

**Model Version**: 1.3  
**Last Updated**: 2024  
**Maintainer**: SentinelAI Team
