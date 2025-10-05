# model_test_v8.py - DEPRECATED
# This file has been replaced by the modular structure:
# - main.py: Main detection system
# - config.py: Configuration settings
# - utils.py: Utility functions
# - detection.py: Weapon detection logic
# - screenshot_manager.py: Screenshot and event management

from ultralytics import YOLO
import cv2
import sys
import os
from datetime import datetime, timedelta
import json
import time
from dotenv import load_dotenv


# Detection Settings
CONFIDENCE_THRESHOLD=0.5
MIN_TIME_BETWEEN_SHOTS=2
EVENT_GROUPING_DURATION=60

# Folder Settings
SCREENSHOT_FOLDER= "weapon_detections"

# Model Settings
MODEL_PATH="best_fine-tuned_model.pt"



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

def setup_folders():
    """
    Create necessary folders for screenshots and events.
    """
    if not os.path.exists(SCREENSHOT_FOLDER):
        os.makedirs(SCREENSHOT_FOLDER)
        print(f"📁 Created folder: {SCREENSHOT_FOLDER}")
    return SCREENSHOT_FOLDER


def save_event_description(event_id, screenshot_paths, event_info):
    """
    Save event metadata to file.
    """
    event_data = {
        "event_id": event_id,
        "timestamp": datetime.now().isoformat(),
        "duration_seconds": event_info.get('duration', 0),
        "screenshot_count": len(screenshot_paths),
        "weapons_detected": event_info.get('weapons', []),
        "screenshot_paths": screenshot_paths
    }
    
    # Save as JSON
    event_file = os.path.join(SCREENSHOT_FOLDER, f"event_{event_id}.json")
    with open(event_file, 'w') as f:
        json.dump(event_data, f, indent=2)
    
    # Save description as text file
    description_file = os.path.join(SCREENSHOT_FOLDER, f"event_{event_id}_description.txt")
    with open(description_file, 'w') as f:
        f.write(f"Security Event - {event_id}\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Timestamp: {event_data['timestamp']}\n")
        f.write(f"Duration: {event_data['duration_seconds']} seconds\n")
        f.write(f"Screenshots: {event_data['screenshot_count']}\n")
        f.write(f"Weapons: {', '.join(event_data['weapons_detected'])}\n\n")
        f.write("Event Summary:\n")
        f.write("-" * 20 + "\n")
        f.write(f"Weapon detection event with {event_data['screenshot_count']} screenshots.\n")
        f.write(f"Weapons detected: {', '.join(event_data['weapons_detected'])}\n")
        f.write(f"Event duration: {event_data['duration_seconds']} seconds\n")
    
    print(f"📝 Event description saved: {description_file}")
    return event_file, description_file

def process_event_group(event_group):
    """
    Process a group of screenshots as one security event.
    """
    if not event_group:
        return
    
    # Use minute-based event ID from the first screenshot
    first_timestamp = min(item['timestamp'] for item in event_group)
    event_id = first_timestamp.strftime("%Y%m%d_%H%M")
    screenshot_paths = [item['filepath'] for item in event_group]
    
    # Calculate event duration
    start_time = min(item['timestamp'] for item in event_group)
    end_time = max(item['timestamp'] for item in event_group)
    duration = (end_time - start_time).total_seconds()
    
    # Collect weapons detected
    all_weapons = set()
    for item in event_group:
        all_weapons.update(item['weapons'])
    
    event_info = {
        'duration': duration,
        'weapons': list(all_weapons),
        'start_time': start_time,
        'end_time': end_time
    }
    
    print(f"\n🔍 Processing Event {event_id}")
    print(f"   Screenshots: {len(screenshot_paths)}")
    print(f"   Duration: {duration:.1f} seconds")
    print(f"   Weapons: {', '.join(all_weapons)}")
    
    # Save event description
    save_event_description(event_id, screenshot_paths, event_info)
    
    # Print summary
    print(f"\n📋 Event Summary:")
    print(f"   Event ID: {event_id}")
    print(f"   Screenshots: {len(screenshot_paths)}")
    print(f"   Weapons: {', '.join(all_weapons)}")

def setup_screenshot_folder():
    """
    Create screenshot folder if it doesn't exist.
    """
    if not os.path.exists(SCREENSHOT_FOLDER):
        os.makedirs(SCREENSHOT_FOLDER)
        print(f"📁 Created screenshot folder: {SCREENSHOT_FOLDER}")
    return SCREENSHOT_FOLDER

def take_screenshot(frame, detection_info, screenshot_count):
    """
    Take a screenshot when weapons are detected.
    """
    # Create timestamp
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Include milliseconds
    
    # Create minute-based event ID for grouping
    minute_event_id = now.strftime("%Y%m%d_%H%M")
    
    # Create filename with detection info and event grouping
    weapons_detected = ", ".join(detection_info['classes'])
    filename = f"event_{minute_event_id}_shot_{screenshot_count:03d}_{weapons_detected}_{timestamp}.jpg"
    
    # Full path
    filepath = os.path.join(SCREENSHOT_FOLDER, filename)
    
    # Save the frame
    cv2.imwrite(filepath, frame)
    
    print(f"📸 Screenshot saved: {filename}")
    print(f"   Event ID: {minute_event_id}")
    print(f"   Weapons detected: {weapons_detected}")
    print(f"   Confidences: {detection_info['confidences']}")
    
    return filepath

def check_weapon_detection(results):
    """
    Check if weapons (pistol/knife) are detected in the results.
    Returns detection info if weapons found, None otherwise.
    """
    if results[0].boxes is None or len(results[0].boxes) == 0:
        return None
    
    weapon_classes = ['pistol', 'knife']  # Your model's classes
    detections = []
    
    for box in results[0].boxes:
        class_id = int(box.cls[0])
        confidence = float(box.conf[0])
        class_name = results[0].names[class_id]
        
        # Check if it's a weapon with sufficient confidence
        if class_name.lower() in weapon_classes and confidence >= CONFIDENCE_THRESHOLD:
            detections.append({
                'class': class_name,
                'confidence': confidence,
                'bbox': box.xyxy[0].tolist()
            })
    
    if detections:
        return {
            'classes': [d['class'] for d in detections],
            'confidences': [f"{d['confidence']:.2f}" for d in detections],
            'detections': detections
        }
    
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

    # Setup folders
    setup_folders()
    
    print(f"\nStarting webcam feed using camera {camera_index}...")
    print("Press 'q' in the video window to quit.")
    print("A window should appear showing your webcam with gun/threat detection.")
    print("📸 Screenshots will be automatically taken when weapons are detected!")
    print(f"📁 Screenshots will be saved to: {SCREENSHOT_FOLDER}/")

    try:
        # Run detection with manual loop for better window control
        print("Starting detection loop...")
        cap = cv2.VideoCapture(camera_index)
        
        if not cap.isOpened():
            print("✗ Failed to open camera for detection")
            return
        
        print("✓ Camera opened successfully for detection")
        print("Press 'q' in the video window to quit, or Ctrl+C in terminal")
        
        # Screenshot tracking variables
        screenshot_count = 0
        last_screenshot_time = 0
        
        # Event grouping variables
        current_event_group = []
        last_event_time = None
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("✗ Failed to read frame from camera")
                break
            
            # Run YOLO prediction on the frame
            results = model(frame, conf=CONFIDENCE_THRESHOLD)
            
            # Check for weapon detection
            detection_info = check_weapon_detection(results)
            current_time = datetime.now().timestamp()
            
            # Take screenshot if weapons detected and enough time has passed
            if detection_info and (current_time - last_screenshot_time) >= MIN_TIME_BETWEEN_SHOTS:
                screenshot_count += 1
                filepath = take_screenshot(frame, detection_info, screenshot_count)
                
                # Add to current event group
                current_event_group.append({
                    'filepath': filepath,
                    'timestamp': datetime.now(),
                    'weapons': detection_info['classes']
                })
                last_screenshot_time = current_time
                last_event_time = current_time
            
            # Draw the results on the frame
            annotated_frame = results[0].plot()
            
            # Add screenshot counter to the frame
            cv2.putText(annotated_frame, f"Screenshots: {screenshot_count}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Display the frame
            cv2.imshow('Gun/Threat Detection', annotated_frame)
            
            # Check if we need to process current event group (1 minute timeout)
            if (current_event_group and last_event_time and 
                (current_time - last_event_time) >= EVENT_GROUPING_DURATION):
                print(f"\n⏰ Event timeout reached ({EVENT_GROUPING_DURATION}s), processing event group...")
                process_event_group(current_event_group)
                current_event_group = []
                last_event_time = None
            
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
        
        # Process any remaining event group
        if 'current_event_group' in locals() and current_event_group:
            print(f"\n🔍 Processing final event group...")
            process_event_group(current_event_group)
        
        # Show screenshot summary
        if 'screenshot_count' in locals() and screenshot_count > 0:
            print(f"\n📸 Session Summary:")
            print(f"   Total screenshots taken: {screenshot_count}")
            print(f"   Screenshots saved to: {SCREENSHOT_FOLDER}/")
            print(f"   Event descriptions saved to: {EVENTS_FOLDER}/")
        else:
            print("\n📸 No weapons detected during this session.")
        
        print("Detection stopped.")


if __name__ == "__main__":
    main()