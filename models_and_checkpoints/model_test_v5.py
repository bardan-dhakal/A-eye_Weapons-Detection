# test_model.py
# A simple script to test your downloaded YOLOv5 model on your computer's webcam.

import cv2
import sys
import yolov5
import numpy as np
import torch
import os

# Fix for PyTorch 2.6+ weights_only issue
torch.serialization.add_safe_globals(['models.yolo.Model'])

# --- CONFIGURATION ---
# Make sure your .pt file is in the same folder as this script,
# or update the path to point to where your file is.
MODEL_PATH = 'model3_yolov5.pt' # Or whatever you named your downloaded YOLOv5 model file

def test_camera_access():
    """
    Test if webcam is accessible by trying to open it with OpenCV.
    """
    print("Testing webcam access...")
    
    # Try different camera indices
    for camera_index in range(5):  # Try cameras 0-4
        try:
            cap = cv2.VideoCapture(camera_index)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    print(f"✓ Camera {camera_index} is working!")
                    cap.release()
                    return camera_index
                cap.release()
        except Exception as e:
            continue
    
    print("✗ No working camera found!")
    print("Troubleshooting tips:")
    print("1. Make sure your webcam is connected and not being used by another application")
    print("2. Try closing other applications that might be using the camera (Skype, Zoom, etc.)")
    print("3. Check Windows camera permissions in Settings > Privacy > Camera")
    print("4. Restart your computer if the camera was recently connected")
    return None

def draw_yolov5_predictions(frame, results, confidence_threshold=0.5):
    """
    Draw YOLOv5 predictions on the frame manually.
    """
    annotated_frame = frame.copy()
    
    # Get predictions from YOLOv5 results
    predictions = results.pred[0]
    
    # YOLOv5 results format: [x1, y1, x2, y2, confidence, class]
    for pred in predictions:
        if len(pred) >= 6:  # Make sure we have all required values
            x1, y1, x2, y2, conf, cls = pred[:6]
            
            # Apply confidence threshold
            if conf > confidence_threshold:
                # Convert to integers
                x1, y1, x2, y2, cls = int(x1), int(y1), int(x2), int(y2), int(cls)
                
                # Choose color based on class (you can customize this)
                colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]
                color = colors[cls % len(colors)]
                
                # Draw bounding box
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
                
                # Draw label with confidence
                label = f"Class {cls}: {conf:.2f}"
                label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
                
                # Draw label background
                cv2.rectangle(annotated_frame, (x1, y1 - label_size[1] - 10), 
                            (x1 + label_size[0], y1), color, -1)
                
                # Draw label text
                cv2.putText(annotated_frame, label, (x1, y1 - 5), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    
    return annotated_frame

def main():
    """
    Main function to run the model test.
    """
    print(f"Loading YOLOv5 model from: {MODEL_PATH}")
    
    try:
        # Load the YOLOv5 model from the .pt file
        model = yolov5.load(MODEL_PATH)
        print("✓ YOLOv5 model loaded successfully!")
    except Exception as e:
        print(f"✗ Error loading YOLOv5 model: {e}")
        print("\nTrying alternative loading method...")
        
        try:
            # Alternative method: load with weights_only=False
            import torch
            # Temporarily disable weights_only for this specific model
            original_load = torch.load
            torch.load = lambda *args, **kwargs: original_load(*args, **kwargs, weights_only=False)
            
            model = yolov5.load(MODEL_PATH)
            print("✓ YOLOv5 model loaded successfully with alternative method!")
            
            # Restore original torch.load
            torch.load = original_load
            
        except Exception as e2:
            print(f"✗ Alternative loading also failed: {e2}")
            print("Please ensure:")
            print("1. The model file is in the same directory as this script")
            print("2. You have yolov5 package installed: pip install yolov5")
            print("3. The model file is a valid YOLOv5 model")
            print("4. You trust the source of this model file")
            return

    # Test camera access before running YOLO
    camera_index = test_camera_access()
    if camera_index is None:
        return

    print(f"\nStarting webcam feed using camera {camera_index}...")
    print("Press 'q' in the video window to quit.")
    print("A window should appear showing your webcam with gun/threat detection.")

    try:
        # Run detection with manual loop for better window control
        print("Starting YOLOv5 detection loop...")
        cap = cv2.VideoCapture(camera_index)
        
        if not cap.isOpened():
            print("✗ Failed to open camera for detection")
            return
        
        print("✓ Camera opened successfully for detection")
        print("Press 'q' in the video window to quit, or Ctrl+C in terminal")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("✗ Failed to read frame from camera")
                break
            
            # Run YOLOv5 prediction on the frame
            results = model(frame)
            
            # Draw the results on the frame using custom function
            annotated_frame = draw_yolov5_predictions(frame, results, confidence_threshold=0.5)
            
            # Display the frame
            cv2.imshow('Gun/Threat Detection (YOLOv5)', annotated_frame)
            
            # Break the loop when 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("Quit key pressed")
                break
                
    except KeyboardInterrupt:
        print("\nInterrupted by user (Ctrl+C)")
    except Exception as e:
        print(f"✗ Error during prediction: {e}")
        print("This might be due to camera access issues or the prediction window being closed.")
    finally:
        # Clean up
        if 'cap' in locals():
            cap.release()
        cv2.destroyAllWindows()
        print("Detection stopped.")


if __name__ == "__main__":
    main()
