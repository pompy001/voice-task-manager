#!/usr/bin/env python3
"""
Simple hotkey test script
"""

import time
import platform
from config import HOTKEY_COMBO

def test_hotkey():
    """Test hotkey functionality"""
    print("="*50)
    print("Simple Hotkey Test")
    print("="*50)
    
    try:
        from pynput import keyboard
        
        # Get hotkey for current OS
        os_name = platform.system().lower()
        hotkey_combo = HOTKEY_COMBO.get(os_name, HOTKEY_COMBO['windows'])
        
        print(f"OS: {platform.system()}")
        print(f"Hotkey combo: {hotkey_combo}")
        
        # Convert string keys to Key objects for pynput
        key_objects = []
        for key_str in hotkey_combo:
            if key_str.lower() in ['ctrl', 'control']:
                key_objects.append(keyboard.Key.ctrl)
            elif key_str.lower() in ['shift']:
                key_objects.append(keyboard.Key.shift)
            elif key_str.lower() in ['alt']:
                key_objects.append(keyboard.Key.alt)
            elif key_str.lower() in ['cmd', 'command']:
                key_objects.append(key_str)  # Keep as string for macOS
            else:
                # Single character key
                key_objects.append(key_str)
        
        print(f"Key objects: {key_objects}")
        
        def on_hotkey():
            print("🎉 HOTKEY PRESSED! It's working!")
        
        print(f"\nSetting up hotkey listener...")
        print("Press Ctrl+Shift+V to test...")
        print("Press Ctrl+C to exit")
        
        # Create hotkey dictionary - pynput expects a tuple of keys
        hotkey_tuple = tuple(key_objects)
        print(f"Hotkey tuple: {hotkey_tuple}")
        
        # Create and start listener
        with keyboard.GlobalHotKeys({hotkey_tuple: on_hotkey}):
            print("✅ Hotkey listener active!")
            print("Waiting for hotkey press...")
            
            # Keep running
            try:
                while True:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                print("\nExiting...")
                
    except ImportError:
        print("❌ pynput not available")
        print("Install with: pip install pynput")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_hotkey()
