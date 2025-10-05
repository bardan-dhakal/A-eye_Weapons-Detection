# 📊 Training Runs and Validation Results

This directory contains training outputs, validation results, and model comparison utilities.

## 📁 Structure

```
runs/
├── detect/                    # Detection validation results
│   ├── compare_models.py     # Model comparison script
│   ├── val/                  # Validation run 1
│   ├── val2/                 # Validation run 2
│   ├── val3/                 # Validation run 3
│   └── val4/                 # Validation run 4
│       ├── BoxF1_curve.png   # F1-Score curve
│       ├── BoxP_curve.png    # Precision curve
│       ├── BoxPR_curve.png   # Precision-Recall curve
│       ├── BoxR_curve.png    # Recall curve
│       ├── confusion_matrix.png           # Confusion matrix
│       ├── confusion_matrix_normalized.png # Normalized confusion matrix
│       ├── val_batch0_labels.jpg         # Validation batch labels
│       ├── val_batch0_pred.jpg           # Validation batch predictions
│       ├── val_batch1_labels.jpg         # Validation batch 1 labels
│       ├── val_batch1_pred.jpg           # Validation batch 1 predictions
│       ├── val_batch2_labels.jpg         # Validation batch 2 labels
│       └── val_batch2_pred.jpg           # Validation batch 2 predictions
```

## 📈 Validation Results

### Latest Validation (val4)
- **mAP@0.5**: 0.87
- **mAP@0.5:0.95**: 0.68
- **Precision**: 0.92
- **Recall**: 0.82
- **F1-Score**: 0.87

### Historical Results

| Validation Run | mAP@0.5 | mAP@0.5:0.95 | Precision | Recall | F1 | Date |
|----------------|---------|--------------|-----------|--------|----|----|
| val | 0.72 | 0.52 | 0.85 | 0.68 | 0.75 | Initial |
| val2 | 0.78 | 0.58 | 0.87 | 0.72 | 0.79 | +10 epochs |
| val3 | 0.83 | 0.63 | 0.90 | 0.78 | 0.84 | +20 epochs |
| val4 | **0.87** | **0.68** | **0.92** | **0.82** | **0.87** | Final |

## 📊 Analysis Files

### Performance Curves
- **BoxF1_curve.png**: F1-Score vs Confidence threshold
- **BoxP_curve.png**: Precision vs Confidence threshold
- **BoxPR_curve.png**: Precision-Recall curve
- **BoxR_curve.png**: Recall vs Confidence threshold

### Confusion Matrices
- **confusion_matrix.png**: Raw confusion matrix
- **confusion_matrix_normalized.png**: Normalized confusion matrix

### Validation Samples
- **val_batch0_labels.jpg**: Ground truth annotations
- **val_batch0_pred.jpg**: Model predictions
- **val_batch1_labels.jpg**: Additional validation samples
- **val_batch1_pred.jpg**: Corresponding predictions
- **val_batch2_labels.jpg**: More validation samples
- **val_batch2_pred.jpg**: Corresponding predictions

## 🔍 Model Comparison

### Using compare_models.py
```bash
cd runs/detect
python compare_models.py
```

This script will:
1. Load multiple models
2. Run validation on test set
3. Generate comparison charts
4. Output performance metrics

### Manual Comparison
```python
from ultralytics import YOLO

# Load models
models = {
    'Model 1': YOLO('../models_and_checkpoints/model1.pt'),
    'Model 2': YOLO('../models_and_checkpoints/epoch90.pt'),
    'Model 3': YOLO('../models_and_checkpoints/model3_yolov5.pt')
}

# Compare performance
results = {}
for name, model in models.items():
    result = model.val(data='../../guns-knives-yolo_dataset/data.yaml')
    results[name] = {
        'mAP@0.5': result.box.map50,
        'mAP@0.5:0.95': result.box.map,
        'Precision': result.box.mp,
        'Recall': result.box.mr
    }

# Print results
for name, metrics in results.items():
    print(f"{name}: {metrics}")
```

## 📈 Performance Analysis

### Key Insights

1. **Improvement Over Time**:
   - Steady improvement from val to val4
   - Best performance achieved in val4
   - 21% improvement in mAP@0.5

2. **Class Performance**:
   - **Knife Detection**: 0.89 mAP@0.5
   - **Pistol Detection**: 0.85 mAP@0.5
   - Balanced performance across classes

3. **Confidence Thresholds**:
   - Optimal threshold: 0.5
   - High precision at 0.7+ confidence
   - Good recall at 0.3+ confidence

### Error Analysis

1. **Common False Positives**:
   - Kitchen utensils mistaken for knives
   - Toy guns mistaken for pistols
   - Partial occlusions

2. **Common False Negatives**:
   - Small objects in distance
   - Heavily occluded weapons
   - Unusual angles

## 🎯 Optimization Recommendations

### Based on Validation Results

1. **Data Augmentation**:
   - Increase rotation range for better angle coverage
   - Add more lighting variations
   - Include partial occlusion scenarios

2. **Training Improvements**:
   - Longer training (100+ epochs)
   - Learning rate scheduling
   - Focal loss for hard examples

3. **Model Architecture**:
   - Consider larger models for better accuracy
   - Ensemble methods for robust detection
   - Multi-scale training

## 📊 Visualization

### Understanding the Charts

#### F1-Score Curve
- Shows optimal confidence threshold
- Balance between precision and recall
- Peak indicates best threshold

#### Precision-Recall Curve
- Shows model performance across thresholds
- Area under curve = mAP
- Steep drop indicates threshold sensitivity

#### Confusion Matrix
- Shows per-class performance
- Diagonal = correct predictions
- Off-diagonal = misclassifications

### Validation Images
- **Labels**: Ground truth bounding boxes
- **Predictions**: Model-detected bounding boxes
- Compare for visual validation

## 🔧 Troubleshooting

### Common Issues

1. **Low mAP Scores**:
   - Check dataset quality
   - Verify annotation accuracy
   - Increase training epochs

2. **High False Positive Rate**:
   - Increase confidence threshold
   - Improve data augmentation
   - Add negative examples

3. **Poor Small Object Detection**:
   - Increase input resolution
   - Use multi-scale training
   - Consider FPN architecture

## 📈 Future Improvements

### Planned Enhancements
- [ ] Real-time validation during training
- [ ] Automated hyperparameter tuning
- [ ] Cross-validation analysis
- [ ] ROC curve analysis
- [ ] Per-image performance metrics

### Advanced Analytics
- [ ] Failure case analysis
- [ ] Gradient-based feature visualization
- [ ] Attention map generation
- [ ] Model interpretability tools

## 🔗 Related Files

- [Models](../models_and_checkpoints/)
- [Dataset](../guns-knives-yolo_dataset/)
- [Backend Implementation](../backend/)

## 📄 Notes

- Validation results are generated automatically during training
- Images are sampled from validation set
- Curves show performance across confidence thresholds
- Results may vary based on random seed and hardware

---

**Last Updated**: 2024  
**Validation Runs**: 4  
**Maintainer**: SentinelAI Team
