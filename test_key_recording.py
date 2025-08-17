#!/usr/bin/env python3
"""
Test script for key-based recording mechanism
"""

import time
import keyboard
from audio_recorder import AudioRecorder

def test_key_recording():
    """Test key-based recording"""
    print("🎤 Key-Based Recording Test")
    print("=" * 40)
    
    recorder = AudioRecorder()
    
    try:
        print("\n1. Press Ctrl+Shift+V to start recording")
        print("2. Speak your task")
        print("3. Press '2' key to stop recording")
        print("4. Wait for processing")
        print("\nPress Ctrl+Shift+V to begin...")
        
        # Wait for hotkey
        keyboard.wait('ctrl+shift+v')
        
        print("\n🎤 Starting recording...")
        print("   Speak your task now!")
        print("   Press '2' to stop recording...")
        
        # Start recording
        audio_file = recorder.start_recording()
        
        if not audio_file:
            print("❌ Failed to start recording")
            return
        
        recording_start_time = time.time()
        max_time = 30
        
        # Wait for stop key or timeout
        while recorder.is_recording():
            if keyboard.is_pressed('2'):
                print("\n⏹️  Stop key '2' pressed!")
                recorder.stop_recording()
                break
            
            if time.time() - recording_start_time > max_time:
                print("\n⏰ Timeout reached!")
                recorder.stop_recording()
                break
            
            time.sleep(0.1)
        
        print("\n✅ Recording stopped!")
        print(f"📁 Audio saved to: {audio_file}")
        
        # Check file
        from pathlib import Path
        if Path(audio_file).exists():
            file_size = Path(audio_file).stat().st_size
            print(f"📊 File size: {file_size} bytes")
            if file_size > 0:
                print("✅ Recording successful!")
            else:
                print("❌ Recording file is empty!")
        else:
            print("❌ Recording file not found!")
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        recorder.cleanup()
        print("\n🧹 Cleanup completed")

if __name__ == "__main__":
    test_key_recording()
