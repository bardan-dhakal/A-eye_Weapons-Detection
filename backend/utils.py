# utils.py
# Utility functions for the Weapons Detection System

import cv2
import os
import sys
from config import *


def test_camera_access():
    """
    Test if webcam is accessible by trying to open it with OpenCV.
    """
    print("Testing webcam access...")
    
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
    Initialize and return a camera object.
    """
    camera_index = test_camera_access()
    if camera_index is None:
        print("❌ No camera available. Exiting...")
        sys.exit(1)
    
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f"❌ Failed to open camera {camera_index}")
        sys.exit(1)
    
    print(f"✓ Camera {camera_index} opened successfully")
    return cap


def cleanup_camera(cap):
    """
    Clean up camera resources.
    """
    if cap:
        cap.release()
    cv2.destroyAllWindows()
