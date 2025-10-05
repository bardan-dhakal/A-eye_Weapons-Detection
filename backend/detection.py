# detection.py
# Weapon detection logic for the Weapons Detection System

import cv2
import os
from ultralytics import YOLO
from config import *


class WeaponDetector:
    """
    Handles weapon detection using YOLO model.
    """
    
    def __init__(self, model_path=MODEL_PATH):
        """
        Initialize the weapon detector with a YOLO model.
        """
        self.model_path = model_path
        self.model = None
        self.load_model()
    
    def load_model(self):
        """
        Load the YOLO model.
        """
        try:
            print(f"🔄 Loading model from {self.model_path}...")
            
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Model file not found: {self.model_path}")
            
            self.model = YOLO(self.model_path)
            print("✅ Model loaded successfully!")
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            raise
    
    def check_weapon_detection(self, results):
        """
        Check if weapons (pistol/knife) are detected in the results.
        Returns detection info if weapons found, None otherwise.
        """
        if not results or len(results) == 0:
            return None
        
        detections = []
        for result in results:
            if result.boxes is not None:
                boxes = result.boxes.xyxy.cpu().numpy()
                confidences = result.boxes.conf.cpu().numpy()
                class_ids = result.boxes.cls.cpu().numpy()
                
                for i, class_id in enumerate(class_ids):
                    class_name = result.names[int(class_id)]
                    confidence = confidences[i]
                    
                    # Check if it's a weapon we're interested in
                    if class_name in WEAPON_CLASSES and confidence >= CONFIDENCE_THRESHOLD:
                        detections.append({
                            'class': class_name,
                            'confidence': float(confidence),
                            'box': boxes[i]
                        })
        
        if detections:
            return {
                'classes': [det['class'] for det in detections],
                'confidences': [det['confidence'] for det in detections],
                'boxes': [det['box'] for det in detections],
                'count': len(detections)
            }
        
        return None
    
    def detect(self, frame):
        """
        Run detection on a frame and return results.
        """
        try:
            results = self.model(frame, verbose=False)
            return results
        except Exception as e:
            print(f"❌ Detection error: {e}")
            return None
    
    def draw_detections(self, frame, detection_info):
        """
        Draw bounding boxes and labels on the frame.
        """
        if not detection_info:
            return frame
        
        annotated_frame = frame.copy()
        
        for i, (box, class_name, confidence) in enumerate(zip(
            detection_info['boxes'],
            detection_info['classes'],
            detection_info['confidences']
        )):
            # Draw bounding box
            x1, y1, x2, y2 = map(int, box)
            color = (0, 0, 255) if class_name == 'pistol' else (255, 0, 0)  # Red for pistol, Blue for knife
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw label
            label = f"{class_name}: {confidence:.2f}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            cv2.rectangle(annotated_frame, (x1, y1 - label_size[1] - 10), 
                         (x1 + label_size[0], y1), color, -1)
            cv2.putText(annotated_frame, label, (x1, y1 - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        return annotated_frame
