# test_model.py
# A simple script to test your downloaded YOLOv8 model on your computer's webcam.

from ultralytics import YOLO
import cv2
import sys

# --- CONFIGURATION ---
# Make sure your .pt file is in the same folder as this script,
# or update the path to point to where your file is.
MODEL_PATH = 'model3_yolov5.pt' # Or whatever you named your downloaded model file

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

def main():
    """
    Main function to run the model test.
    """
    print(f"Loading model from: {MODEL_PATH}")
    
    try:
        # Load the YOLOv8 model from the .pt file
        model = YOLO(MODEL_PATH)
        print("✓ Model loaded successfully!")
    except Exception as e:
        print(f"✗ Error loading model: {e}")
        print("Please ensure the model file is in the same directory as this script.")
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
        print("Starting detection loop...")
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
            
            # Run YOLO prediction on the frame
            results = model(frame, conf=0.5)
            
            # Draw the results on the frame
            annotated_frame = results[0].plot()
            
            # Display the frame
            cv2.imshow('Gun/Threat Detection', annotated_frame)
            
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
