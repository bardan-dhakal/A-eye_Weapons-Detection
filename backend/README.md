# Weapons Detection System - Backend

This is a modular weapon detection system that uses YOLO models to detect knives and pistols in real-time video streams.

## File Structure

```
backend/
├── main.py                 # Main detection system (entry point)
├── config.py              # Configuration settings and constants
├── utils.py               # Utility functions (camera, folders)
├── detection.py           # Weapon detection logic and YOLO model handling
├── screenshot_manager.py  # Screenshot capture and event management
├── model_test_v8.py       # Legacy file (deprecated)
├── requirements.txt       # Python dependencies
└── weapon_detections/     # Output folder for screenshots and events
```

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the detection system:**
   ```bash
   python main.py
   ```

3. **Controls:**
   - Press `q` or `ESC` to quit
   - Screenshots are automatically taken when weapons are detected

## Configuration

All settings can be configured in `config.py` or via environment variables:

- `CONFIDENCE_THRESHOLD`: Detection confidence threshold (default: 0.5)
- `MIN_TIME_BETWEEN_SHOTS`: Minimum seconds between screenshots (default: 2)
- `MODEL_PATH`: Path to YOLO model file (default: 'best_fine-tuned_model.pt')
- `SCREENSHOT_FOLDER`: Output folder for screenshots (default: 'weapon_detections')

## Modules Overview

### main.py
- Entry point for the detection system
- Orchestrates all components
- Handles the main detection loop

### config.py
- Centralized configuration
- Environment variable loading
- System constants and settings

### utils.py
- Camera access and testing
- Folder setup utilities
- Resource cleanup functions

### detection.py
- YOLO model loading and management
- Weapon detection logic
- Bounding box drawing and visualization

### screenshot_manager.py
- Screenshot capture and naming
- Event grouping (by minute)
- Metadata and summary file generation

## Event Grouping

Screenshots are automatically grouped into events:
- All screenshots taken within the same minute = one event
- Event files are saved with minute-based IDs (e.g., `event_20250104_1430`)
- Each event includes JSON metadata and text summary files

## Output Files

The system creates the following files in `weapon_detections/`:
- `event_YYYYMMDD_HHMM_shot_XXX_weapon_timestamp.jpg` - Screenshots
- `event_YYYYMMDD_HHMM.json` - Event metadata (JSON)
- `event_YYYYMMDD_HHMM_description.txt` - Event summary (text)

## Legacy Support

The original `model_test_v8.py` file is kept for reference but is deprecated. Use `main.py` for the new modular system.