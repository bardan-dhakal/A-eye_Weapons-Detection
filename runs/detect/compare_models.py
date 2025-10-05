# compare_models.py
# Compare accuracy of newly trained models vs base model

from ultralytics import YOLO
import os

def compare_model_accuracy():
    """
    Compare accuracy of different models on the same dataset
    """
    print("🔄 Comparing Model Accuracy")
    print("=" * 50)
    
    # Define models to compare
    models_to_compare = [
        {
            'name': 'Base Model',
            'path': 'model1.pt'
        },
        {
            'name': 'Epoch 10 Fine-tuned',
            'path': 'epoch10_fine_tuning.pt'
        }
    ]
    
    # Create corrected dataset path for local testing
    dataset_base = 'guns-knives-yolo/guns-knives-yolo'
    
    # Create corrected yaml content for local paths
    yaml_content = f"""
path: {os.path.abspath(dataset_base)}
train: train/images
val: valid/images

nc: 2
names: ["knife", "pistol"]
"""
    
    # Save corrected yaml
    corrected_yaml_path = 'corrected_dataset.yaml'
    with open(corrected_yaml_path, 'w') as f:
        f.write(yaml_content.strip())
    
    dataset_path = corrected_yaml_path
    print(f"📁 Using corrected dataset paths: {dataset_path}")
    
    results = []
    
    for model_info in models_to_compare:
        model_name = model_info['name']
        model_path = model_info['path']
        
        print(f"\n🧪 Testing: {model_name}")
        print(f"📁 Model: {model_path}")
        
        if not os.path.exists(model_path):
            print(f"❌ Model not found: {model_path}")
            continue
        
        try:
            # Load model
            model = YOLO(model_path)
            
            # Run validation
            print("📊 Running validation...")
            val_results = model.val(
                data=dataset_path,
                conf=0.25,
                iou=0.7,
                verbose=False  # Less verbose output
            )
            
            # Extract metrics
            metrics = {
                'model_name': model_name,
                'model_path': model_path,
                'mAP50': float(val_results.box.map50),
                'mAP50-95': float(val_results.box.map),
                'precision': float(val_results.box.mp),
                'recall': float(val_results.box.mr)
            }
            
            results.append(metrics)
            
            print(f"✅ Results:")
            print(f"  mAP50: {metrics['mAP50']:.3f}")
            print(f"  mAP50-95: {metrics['mAP50-95']:.3f}")
            print(f"  Precision: {metrics['precision']:.3f}")
            print(f"  Recall: {metrics['recall']:.3f}")
            
        except Exception as e:
            print(f"❌ Error testing {model_name}: {e}")
    
    # Print comparison summary
    if len(results) >= 2:
        print(f"\n📊 ACCURACY COMPARISON SUMMARY")
        print("=" * 60)
        print(f"{'Model':<20} {'mAP50':<8} {'mAP50-95':<8} {'Precision':<10} {'Recall':<8}")
        print("-" * 60)
        
        for result in results:
            print(f"{result['model_name']:<20} {result['mAP50']:<8.3f} {result['mAP50-95']:<8.3f} {result['precision']:<10.3f} {result['recall']:<8.3f}")
        
        # Calculate improvements
        base_model = results[0]  # Assuming first is base model
        improved_model = results[1]  # Assuming second is improved model
        
        print(f"\n📈 IMPROVEMENT ANALYSIS")
        print("-" * 40)
        
        mAP50_improvement = improved_model['mAP50'] - base_model['mAP50']
        mAP50_95_improvement = improved_model['mAP50-95'] - base_model['mAP50-95']
        precision_improvement = improved_model['precision'] - base_model['precision']
        recall_improvement = improved_model['recall'] - base_model['recall']
        
        print(f"mAP50 improvement: {mAP50_improvement:+.3f} ({mAP50_improvement/base_model['mAP50']*100:+.1f}%)")
        print(f"mAP50-95 improvement: {mAP50_95_improvement:+.3f} ({mAP50_95_improvement/base_model['mAP50-95']*100:+.1f}%)")
        print(f"Precision improvement: {precision_improvement:+.3f} ({precision_improvement/base_model['precision']*100:+.1f}%)")
        print(f"Recall improvement: {recall_improvement:+.3f} ({recall_improvement/base_model['recall']*100:+.1f}%)")
        
        # Overall assessment
        overall_improvement = (mAP50_improvement + mAP50_95_improvement) / 2
        
        print(f"\n🎯 OVERALL ASSESSMENT")
        print("-" * 25)
        if overall_improvement > 0.05:
            print("🏆 SIGNIFICANT IMPROVEMENT! Your training was very successful!")
        elif overall_improvement > 0.02:
            print("✅ GOOD IMPROVEMENT! Your training was successful.")
        elif overall_improvement > 0:
            print("👍 SLIGHT IMPROVEMENT! Training helped a bit.")
        else:
            print("⚠️  NO IMPROVEMENT. You may need more training data or different parameters.")
        
        print(f"Overall mAP improvement: {overall_improvement:+.3f}")
    
    return results

if __name__ == "__main__":
    results = compare_model_accuracy()
