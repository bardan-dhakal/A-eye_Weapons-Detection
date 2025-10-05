# main.py
# Main weapon detection system - orchestrates all components

import cv2
import sys
from config import *
from utils import setup_folders, get_camera, cleanup_camera
from detection import WeaponDetector
from screenshot_manager import ScreenshotManager


def main():
    """
    Main function to run the weapon detection system.
    """
    print("🔫 Weapons Detection System Starting...")
    print("=" * 50)
    
    # Setup folders
    setup_folders()
    
    # Initialize components
    print("\n🔄 Initializing components...")
    
    # Initialize weapon detector
    try:
        detector = WeaponDetector(MODEL_PATH)
    except Exception as e:
        print(f"❌ Failed to initialize weapon detector: {e}")
        sys.exit(1)
    
    # Initialize screenshot manager
    screenshot_manager = ScreenshotManager()
    
    # Initialize camera
    cap = get_camera()
    
    print("\n✅ All components initialized successfully!")
    print(f"📁 Screenshots will be saved to: {SCREENSHOT_FOLDER}")
    print(f"🎯 Detection threshold: {CONFIDENCE_THRESHOLD}")
    print(f"⏱️  Min time between shots: {MIN_TIME_BETWEEN_SHOTS} seconds")
    print("\n🎥 Starting detection...")
    print("Press 'q' to quit, 'ESC' to exit")
    print("-" * 50)
    
    try:
        while True:
            # Capture frame
            ret, frame = cap.read()
            if not ret:
                print("❌ Failed to read frame from camera")
                break
            
            # Run detection
            results = detector.detect(frame)
            if results is None:
                continue
            
            # Check for weapon detections
            detection_info = detector.check_weapon_detection(results)
            
            # Draw detections on frame
            if detection_info:
                frame = detector.draw_detections(frame, detection_info)
                
                # Take screenshot if weapons detected
                screenshot_manager.take_screenshot(frame, detection_info)
            
            # Display frame
            cv2.imshow(WINDOW_NAME, frame)
            
            # Check for exit
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == ESC_KEY:
                print("\n🛑 Exiting detection...")
                break
    
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user...")
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    
    finally:
        # Process any remaining screenshots
        print("\n📸 Processing final screenshots...")
        screenshot_manager.process_pending_screenshots()
        
        # Cleanup
        print("🧹 Cleaning up...")
        cleanup_camera(cap)
        
        print("✅ System shutdown complete!")



if __name__ == "__main__":
    main()
