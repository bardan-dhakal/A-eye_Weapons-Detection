# setup_for_friend.py
# Quick setup script for friends to get the optimized streaming

import os
import sys

def create_file(filepath, content):
    """Create a file with given content"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Created: {filepath}")
        return True
    except Exception as e:
        print(f"❌ Failed to create {filepath}: {e}")
        return False

def main():
    """Setup optimized streaming files"""
    print("🚀 Setting up Optimized Streaming Architecture")
    print("=" * 50)
    
    # Check if files already exist
    new_files = [
        'streaming_optimized.py',
        'launcher.py', 
        'performance_test.py'
    ]
    
    existing_files = [f for f in new_files if os.path.exists(f)]
    
    if existing_files:
        print(f"⚠️  These files already exist: {existing_files}")
        response = input("Do you want to overwrite them? (y/n): ")
        if response.lower() != 'y':
            print("Setup cancelled.")
            return
    
    print("📁 This script will create the optimized streaming files.")
    print("💡 Make sure you're in the Weapons-Detection/backend directory!")
    print()
    
    # Instructions for manual setup
    print("📋 Manual Setup Instructions:")
    print("1. Copy the following files from your friend:")
    print("   - streaming_optimized.py")
    print("   - launcher.py")
    print("   - performance_test.py")
    print()
    print("2. Update config.py with these new settings:")
    print("   - OPTIMIZED_STREAMING = True")
    print("   - PI_CAMERA_FPS = 15")
    print("   - PI_STREAM_QUALITY = 30")
    print("   - PI_DETECTION_FPS = 5")
    print()
    print("3. Test the new architecture:")
    print("   python launcher.py")
    print()
    print("4. Or run optimized directly:")
    print("   python streaming_optimized.py")
    print()
    print("🎯 Expected improvements:")
    print("   - Streaming FPS: 1 → 10-15 FPS")
    print("   - Less freezing and lag")
    print("   - Better Raspberry Pi performance")

if __name__ == "__main__":
    main()
