# utils.py
# Utility functions for the Weapons Detection System

import cv2
import os
import sys
import platform
from config import *


def test_camera_access():
    """
    Test if webcam is accessible by trying to open it with OpenCV.
    Supports both regular webcams and Raspberry Pi cameras.
    """
    print("Testing camera access...")
    
    # First try Raspberry Pi camera device if specified
    if CAMERA_DEVICE and CAMERA_DEVICE.startswith('/dev/video'):
        print(f"Testing Raspberry Pi camera: {CAMERA_DEVICE}")
        cap = cv2.VideoCapture(CAMERA_DEVICE)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"✓ Raspberry Pi camera {CAMERA_DEVICE} is accessible")
                cap.release()
                return CAMERA_DEVICE
            cap.release()
        print(f"✗ Raspberry Pi camera {CAMERA_DEVICE} is not accessible")
    
    # Fall back to regular camera indices
    print("Testing regular camera indices...")
    for camera_index in range(MAX_CAMERA_INDEX):
        cap = cv2.VideoCapture(camera_index)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"✓ Camera {camera_index} is accessible")
                cap.release()
                return camera_index
            cap.release()
        else:
            print(f"✗ Camera {camera_index} is not accessible")
    
    print("❌ No accessible camera found!")
    return None


def is_raspberry_pi():
    """
    Check if running on a Raspberry Pi.
    """
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
            return 'BCM' in cpuinfo or 'Raspberry Pi' in cpuinfo
    except:
        return False


def get_optimal_camera_settings():
    """
    Get optimal camera settings based on the platform.
    """
    if is_raspberry_pi():
        print("🍓 Detected Raspberry Pi - using optimized settings")
        return {
            'width': CAMERA_WIDTH,
            'height': CAMERA_HEIGHT,
            'fps': min(CAMERA_FPS, 20),  # Limit FPS on Pi for better performance
            'buffer_size': 1  # Reduce buffer for lower latency
        }
    else:
        print("💻 Detected regular computer - using standard settings")
        return {
            'width': CAMERA_WIDTH,
            'height': CAMERA_HEIGHT,
            'fps': CAMERA_FPS,
            'buffer_size': 3
        }


def setup_folders():
    """
    Create necessary folders for screenshots.
    """
    if not os.path.exists(SCREENSHOT_FOLDER):
        os.makedirs(SCREENSHOT_FOLDER)
        print(f"📁 Created folder: {SCREENSHOT_FOLDER}")
    return SCREENSHOT_FOLDER


def get_camera():
    """
    Initialize and return a camera object with optimal settings.
    """
    camera_device = test_camera_access()
    if camera_device is None:
        print("❌ No camera available. Exiting...")
        sys.exit(1)
    
    cap = cv2.VideoCapture(camera_device)
    if not cap.isOpened():
        print(f"❌ Failed to open camera {camera_device}")
        sys.exit(1)
    
    # Apply optimal camera settings
    settings = get_optimal_camera_settings()
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, settings['width'])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, settings['height'])
    cap.set(cv2.CAP_PROP_FPS, settings['fps'])
    cap.set(cv2.CAP_PROP_BUFFERSIZE, settings['buffer_size'])
    
    # Verify settings were applied
    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    actual_fps = cap.get(cv2.CAP_PROP_FPS)
    
    print(f"✓ Camera {camera_device} opened successfully")
    print(f"   Resolution: {actual_width}x{actual_height}")
    print(f"   FPS: {actual_fps}")
    print(f"   Platform: {'Raspberry Pi' if is_raspberry_pi() else 'Regular Computer'}")
    
    return cap


def cleanup_camera(cap):
    """
    Clean up camera resources.
    """
    if cap:
        cap.release()
    cv2.destroyAllWindows()
