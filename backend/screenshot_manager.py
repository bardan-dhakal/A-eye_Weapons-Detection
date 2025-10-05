# screenshot_manager.py
# Screenshot and event management for the Weapons Detection System

import cv2
import os
import json
import time
from datetime import datetime, timedelta
from config import *


class ScreenshotManager:
    """
    Handles screenshot capture and event grouping.
    """
    
    def __init__(self):
        """
        Initialize the screenshot manager.
        """
        self.screenshot_count = 0
        self.last_screenshot_time = None
        self.pending_screenshots = []
        
    def can_take_screenshot(self):
        """
        Check if enough time has passed since the last screenshot.
        """
        if self.last_screenshot_time is None:
            return True
        
        time_since_last = (datetime.now() - self.last_screenshot_time).total_seconds()
        return time_since_last >= MIN_TIME_BETWEEN_SHOTS
    
    def take_screenshot(self, frame, detection_info):
        """
        Take a screenshot when weapons are detected.
        """
        if not self.can_take_screenshot():
            return None
        
        # Create timestamp
        now = datetime.now()
        timestamp = now.strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Include milliseconds
        
        # Create minute-based event ID for grouping
        minute_event_id = now.strftime("%Y%m%d_%H%M")
        
        # Create filename with detection info and event grouping
        weapons_detected = ", ".join(detection_info['classes'])
        filename = f"event_{minute_event_id}_shot_{self.screenshot_count:03d}_{weapons_detected}_{timestamp}.jpg"
        
        # Full path
        filepath = os.path.join(SCREENSHOT_FOLDER, filename)
        
        # Save the frame
        cv2.imwrite(filepath, frame)
        
        self.screenshot_count += 1
        self.last_screenshot_time = now
        
        print(f"📸 Screenshot saved: {filename}")
        print(f"   Event ID: {minute_event_id}")
        print(f"   Weapons detected: {weapons_detected}")
        print(f"   Confidences: {detection_info['confidences']}")
        
        # Add to pending screenshots for event grouping
        self.pending_screenshots.append({
            'filepath': filepath,
            'timestamp': now,
            'weapons': detection_info['classes'],
            'confidences': detection_info['confidences']
        })
        
        return filepath
    
    def save_event_description(self, event_id, screenshot_paths, event_info):
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
    
    def process_event_group(self, event_group):
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
        self.save_event_description(event_id, screenshot_paths, event_info)
        
        # Print summary
        print(f"\n📋 Event Summary:")
        print(f"   Event ID: {event_id}")
        print(f"   Screenshots: {len(screenshot_paths)}")
        print(f"   Weapons: {', '.join(all_weapons)}")
    
    def process_pending_screenshots(self):
        """
        Process all pending screenshots and group them into events.
        """
        if not self.pending_screenshots:
            return
        
        # Group screenshots by minute
        current_group = []
        current_minute = None
        
        for screenshot in self.pending_screenshots:
            screenshot_minute = screenshot['timestamp'].strftime("%Y%m%d_%H%M")
            
            if current_minute is None or screenshot_minute == current_minute:
                current_group.append(screenshot)
                current_minute = screenshot_minute
            else:
                # Process the current group
                self.process_event_group(current_group)
                # Start new group
                current_group = [screenshot]
                current_minute = screenshot_minute
        
        # Process the last group
        if current_group:
            self.process_event_group(current_group)
        
        # Clear pending screenshots
        self.pending_screenshots = []
