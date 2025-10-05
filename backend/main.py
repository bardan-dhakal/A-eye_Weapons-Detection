# main.py
# Main weapon detection system - orchestrates all components

import cv2
import sys
import time
from threading import Thread
from config import *
from utils import setup_folders, get_camera, cleanup_camera
from detection import WeaponDetector
from screenshot_manager import ScreenshotManager
from streaming_server import set_detector, update_streaming_frame, start_server


def main():
    """
    Main function to run the weapon detection system with streaming support.
    """
    print("🛡️ SentinelAI Weapons Detection System Starting...")
    print("=" * 60)
    
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
    
    # Setup streaming server if enabled
    streaming_thread = None
    if STREAMING_ENABLED:
        print("\n🌐 Setting up streaming server...")
        set_detector(detector, screenshot_manager)
        streaming_thread = Thread(target=start_server, daemon=True)
        streaming_thread.start()
        print("✅ Streaming server started in background")
    
    print("\n✅ All components initialized successfully!")
    print(f"📁 Screenshots will be saved to: {SCREENSHOT_FOLDER}")
    print(f"🎯 Detection threshold: {CONFIDENCE_THRESHOLD}")
    print(f"⏱️  Min time between shots: {MIN_TIME_BETWEEN_SHOTS} seconds")
    if STREAMING_ENABLED:
        print(f"🌐 Web dashboard: http://{SERVER_HOST}:{SERVER_PORT}/")
    print("\n🎥 Starting detection...")
    if not STREAMING_ENABLED:
        print("Press 'q' to quit, 'ESC' to exit")
    print("-" * 60)
    
    # Performance tracking
    frame_count = 0
    total_detections = 0
    start_time = time.time()
    frame_skip_counter = 0  # For detection frame skipping
    stream_skip_counter = 0  # For streaming frame skipping
    
    try:
        while True:
            # Capture frame
            ret, frame = cap.read()
            if not ret:
                print("❌ Failed to read frame from camera")
                break
            
            frame_count += 1
            
            # Update streaming frame with additional skipping for performance
            if STREAMING_ENABLED:
                stream_skip_counter += 1
                if stream_skip_counter > STREAMING_SKIP_FRAMES:
                    stream_skip_counter = 0
                    elapsed = time.time() - start_time
                    fps = frame_count / elapsed if elapsed > 0 else 0
                    # Send raw frame first (no detection overlay for maximum speed)
                    update_streaming_frame(frame, None, fps, frame_count, total_detections)
            
            # Skip detection on some frames for better performance
            frame_skip_counter += 1
            if frame_skip_counter >= DETECTION_SKIP_FRAMES:
                frame_skip_counter = 0
                
                # Run detection only every few frames
                results = detector.detect(frame)
                if results is not None:
                    # Check for weapon detections
                    detection_info = detector.check_weapon_detection(results)
                    
                    # Draw detections on frame
                    if detection_info:
                        frame_with_detections = detector.draw_detections(frame, detection_info)
                        
                        # Take screenshot if weapons detected
                        screenshot_manager.take_screenshot(frame_with_detections, detection_info)
                        total_detections += 1
                        
                        # Update streaming with detection overlay (optional)
                        if STREAMING_ENABLED:
                            update_streaming_frame(frame_with_detections, detection_info, fps, frame_count, total_detections)
            
            # Display frame only if streaming is disabled
            if not STREAMING_ENABLED:
                cv2.imshow(WINDOW_NAME, frame)
                
                # Check for exit
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == ESC_KEY:
                    print("\n🛑 Exiting detection...")
                    break
            else:
                # Small delay to prevent overwhelming CPU when streaming
                time.sleep(0.01)
    
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
        
        # Print final statistics
        if frame_count > 0:
            elapsed = time.time() - start_time
            avg_fps = frame_count / elapsed if elapsed > 0 else 0
            detection_fps = (frame_count // (DETECTION_SKIP_FRAMES + 1)) / elapsed if elapsed > 0 else 0
            print(f"\n📊 Final Statistics:")
            print(f"   Total frames processed: {frame_count}")
            print(f"   Total weapon detections: {total_detections}")
            print(f"   Average FPS: {avg_fps:.2f}")
            print(f"   Detection FPS: {detection_fps:.2f}")
            print(f"   Stream max FPS: {STREAM_MAX_FPS}")
            print(f"   Detection skip frames: {DETECTION_SKIP_FRAMES}")
            print(f"   Runtime: {elapsed:.2f} seconds")
        
        print("✅ System shutdown complete!")



if __name__ == "__main__":
    main()
