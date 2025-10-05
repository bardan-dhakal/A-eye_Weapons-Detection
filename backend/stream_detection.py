# stream_detection_server.py
# Flask server to stream AI detection feed to frontend

from flask import Flask, Response, jsonify, render_template_string
from flask_cors import CORS
from ultralytics import YOLO
import cv2
import numpy as np
import time
import json
from threading import Thread, Lock
from pathlib import Path

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# --- CONFIGURATION ---
MODEL_PATH = 'best_fine-tuned_model.pt'
CAMERA_DEVICE = '/dev/video2'
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CONFIDENCE_THRESHOLD = 0.5
SERVER_PORT = 5000

# Global variables
model = None
camera = None
current_frame = None
detection_data = {
    'threats': [],
    'count': 0,
    'fps': 0,
    'frame_count': 0,
    'status': 'initializing'
}
frame_lock = Lock()
data_lock = Lock()

def initialize_model():
    """Load YOLO model"""
    global model
    try:
        print(f"[INIT] Loading model: {MODEL_PATH}")
        model = YOLO(MODEL_PATH)
        print("[INIT] ✓ Model loaded successfully")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to load model: {e}")
        return False

def initialize_camera():
    """Initialize camera"""
    global camera
    try:
        print(f"[INIT] Opening camera: {CAMERA_DEVICE}")
        camera = cv2.VideoCapture(CAMERA_DEVICE if isinstance(CAMERA_DEVICE, int) else CAMERA_DEVICE)
        
        if not camera.isOpened():
            print("[ERROR] Failed to open camera")
            return False
        
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        camera.set(cv2.CAP_PROP_FPS, 30)
        
        print("[INIT] ✓ Camera initialized")
        return True
    except Exception as e:
        print(f"[ERROR] Camera initialization failed: {e}")
        return False

def detection_loop():
    """Main detection loop running in background thread"""
    global current_frame, detection_data
    
    frame_count = 0
    start_time = time.time()
    total_detections = 0
    
    print("[DETECTION] Starting detection loop...")
    
    while True:
        try:
            ret, frame = camera.read()
            
            if not ret or frame is None:
                with data_lock:
                    detection_data['status'] = 'camera_error'
                time.sleep(0.1)
                continue
            
            frame_count += 1
            
            # Run YOLO detection
            results = model(frame, conf=CONFIDENCE_THRESHOLD, verbose=False)
            boxes = results[0].boxes
            
            # Parse detections
            threats = []
            if len(boxes) > 0:
                total_detections += 1
                for box in boxes:
                    threats.append({
                        'class': results[0].names[int(box.cls[0])],
                        'confidence': float(box.conf[0]),
                        'bbox': box.xyxy[0].cpu().numpy().tolist()
                    })
            
            # Annotate frame
            annotated_frame = results[0].plot()
            
            # Calculate FPS
            elapsed = time.time() - start_time
            fps = frame_count / elapsed if elapsed > 0 else 0
            
            # Add overlay info
            overlay_text = [
                f"FPS: {fps:.1f}",
                f"Frame: {frame_count}",
                f"Threats: {total_detections}",
                f"Current: {len(boxes)} detected" if len(boxes) > 0 else "Status: Clear"
            ]
            
            y_offset = 30
            for i, text in enumerate(overlay_text):
                color = (0, 255, 0) if len(boxes) == 0 else (0, 0, 255)
                cv2.putText(annotated_frame, text, (10, y_offset + i * 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            
            # Update global state
            with frame_lock:
                current_frame = annotated_frame.copy()
            
            with data_lock:
                detection_data = {
                    'threats': threats,
                    'count': len(boxes),
                    'fps': round(fps, 2),
                    'frame_count': frame_count,
                    'total_detections': total_detections,
                    'status': 'threat_detected' if len(boxes) > 0 else 'monitoring',
                    'timestamp': time.time()
                }
            
            # Small delay to prevent overwhelming CPU
            time.sleep(0.01)
            
        except Exception as e:
            print(f"[ERROR] Detection loop error: {e}")
            with data_lock:
                detection_data['status'] = 'error'
            time.sleep(1)

def generate_frames():
    """Generator function for video streaming"""
    while True:
        with frame_lock:
            if current_frame is None:
                continue
            frame = current_frame.copy()
        
        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        
        if not ret:
            continue
        
        frame_bytes = buffer.tobytes()
        
        # Yield frame in multipart format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

# --- API ENDPOINTS ---

@app.route('/')
def index():
    """Simple test page"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SentinelAI - Detection Stream</title>
        <style>
            body {
                margin: 0;
                padding: 20px;
                background: #1a1a1a;
                color: white;
                font-family: Arial, sans-serif;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            h1 {
                text-align: center;
                color: #00ff00;
            }
            .video-container {
                text-align: center;
                margin: 20px 0;
            }
            img {
                max-width: 100%;
                border: 3px solid #00ff00;
                border-radius: 8px;
            }
            .stats {
                background: #2a2a2a;
                padding: 20px;
                border-radius: 8px;
                margin-top: 20px;
            }
            .stat-item {
                margin: 10px 0;
                font-size: 18px;
            }
            .threat {
                color: #ff0000;
                font-weight: bold;
            }
            .clear {
                color: #00ff00;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🛡️ SentinelAI - Real-Time Threat Detection</h1>
            
            <div class="video-container">
                <img src="/video_feed" alt="Detection Feed">
            </div>
            
            <div class="stats" id="stats">
                <div class="stat-item">Status: <span id="status">Loading...</span></div>
                <div class="stat-item">FPS: <span id="fps">0</span></div>
                <div class="stat-item">Frame Count: <span id="frames">0</span></div>
                <div class="stat-item">Total Detections: <span id="total">0</span></div>
                <div class="stat-item">Current Threats: <span id="current">0</span></div>
            </div>
        </div>
        
        <script>
            // Update stats every second
            setInterval(() => {
                fetch('/api/status')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('status').textContent = data.status;
                        document.getElementById('status').className = 
                            data.status === 'threat_detected' ? 'threat' : 'clear';
                        document.getElementById('fps').textContent = data.fps;
                        document.getElementById('frames').textContent = data.frame_count;
                        document.getElementById('total').textContent = data.total_detections || 0;
                        document.getElementById('current').textContent = data.count;
                    })
                    .catch(err => console.error('Error fetching status:', err));
            }, 1000);
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/status')
def get_status():
    """Get current detection status"""
    with data_lock:
        return jsonify(detection_data)

@app.route('/api/threats')
def get_threats():
    """Get current threat detections"""
    with data_lock:
        return jsonify({
            'threats': detection_data.get('threats', []),
            'count': detection_data.get('count', 0),
            'timestamp': detection_data.get('timestamp', 0)
        })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None,
        'camera_active': camera is not None and camera.isOpened()
    })

def main():
    """Initialize and start server"""
    print("="*60)
    print("SentinelAI - Detection Streaming Server")
    print("="*60)
    
    # Initialize model
    if not initialize_model():
        print("[ERROR] Failed to initialize model. Exiting.")
        return
    
    # Initialize camera
    if not initialize_camera():
        print("[ERROR] Failed to initialize camera. Exiting.")
        return
    
    # Start detection thread
    detection_thread = Thread(target=detection_loop, daemon=True)
    detection_thread.start()
    
    print(f"\n[SERVER] Starting Flask server on http://0.0.0.0:{SERVER_PORT}")
    print(f"[SERVER] Video feed: http://0.0.0.0:{SERVER_PORT}/video_feed")
    print(f"[SERVER] API status: http://0.0.0.0:{SERVER_PORT}/api/status")
    print(f"[SERVER] Test page: http://0.0.0.0:{SERVER_PORT}/")
    print("\n[SERVER] Press Ctrl+C to stop\n")
    print("="*60 + "\n")
    
    try:
        app.run(host='0.0.0.0', port=SERVER_PORT, threaded=True, debug=False)
    except KeyboardInterrupt:
        print("\n[SERVER] Shutting down...")
    finally:
        if camera:
            camera.release()
        print("[SERVER] Stopped")

if __name__ == '__main__':
    main()
