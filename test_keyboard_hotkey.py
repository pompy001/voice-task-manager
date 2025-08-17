#!/usr/bin/env python3
"""
Hotkey test using keyboard library (more reliable on Windows)
"""

import time
import platform
from config import HOTKEY_COMBO

def test_keyboard_hotkey():
    """Test hotkey functionality using keyboard library"""
    print("="*50)
    print("Keyboard Library Hotkey Test")
    print("="*50)
    
    try:
        import keyboard
        
        # Get hotkey for current OS
        os_name = platform.system().lower()
        hotkey_combo = HOTKEY_COMBO.get(os_name, HOTKEY_COMBO['windows'])
        
        print(f"OS: {platform.system()}")
        print(f"Hotkey combo: {hotkey_combo}")
        
        # Convert to keyboard library format
        hotkey_string = '+'.join(hotkey_combo)
        print(f"Hotkey string: {hotkey_string}")
        
        def on_hotkey():
            print("🎉 HOTKEY PRESSED! It's working!")
        
        print(f"\nSetting up hotkey: {hotkey_string}")
        print("Press Ctrl+Shift+V to test...")
        print("Press Ctrl+C to exit")
        
        # Register the hotkey
        keyboard.add_hotkey(hotkey_string, on_hotkey)
        print("✅ Hotkey listener active!")
        print("Waiting for hotkey press...")
        
        # Keep running
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nExiting...")
            keyboard.unhook_all()
                
    except ImportError:
        print("❌ keyboard library not available")
        print("Install with: pip install keyboard")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_keyboard_hotkey()
