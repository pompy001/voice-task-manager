#!/usr/bin/env python3
"""
Test script for hotkey functionality
"""

import platform
import sys
from config import HOTKEY_COMBO

def test_hotkey_config():
    """Test hotkey configuration"""
    print("="*50)
    print("Hotkey Configuration Test")
    print("="*50)
    
    # Check OS
    os_name = platform.system().lower()
    print(f"Operating System: {platform.system()} ({os_name})")
    
    # Check hotkey config
    print(f"Hotkey Configuration: {HOTKEY_COMBO}")
    
    # Get appropriate hotkey for current OS
    if os_name in HOTKEY_COMBO:
        hotkey = HOTKEY_COMBO[os_name]
        print(f"Hotkey for {os_name}: {'+'.join(hotkey)}")
    else:
        print(f"No specific config for {os_name}, using Windows default")
        hotkey = HOTKEY_COMBO['windows']
        print(f"Default hotkey: {'+'.join(hotkey)}")
    
    # Test pynput import
    try:
        from pynput import keyboard
        print("✅ pynput imported successfully")
        
        # Test key conversion
        key_objects = []
        for key_str in hotkey:
            if key_str.lower() in ['ctrl', 'control']:
                key_objects.append(keyboard.Key.ctrl)
                print(f"  {key_str} -> {keyboard.Key.ctrl}")
            elif key_str.lower() in ['shift']:
                key_objects.append(keyboard.Key.shift)
                print(f"  {key_str} -> {keyboard.Key.shift}")
            elif key_str.lower() in ['alt']:
                key_objects.append(keyboard.Key.alt)
                print(f"  {key_str} -> {keyboard.Key.alt}")
            elif key_str.lower() in ['cmd', 'command']:
                key_objects.append(keyboard.Key.cmd)
                print(f"  {key_str} -> {keyboard.Key.cmd}")
            else:
                key_objects.append(key_str)
                print(f"  {key_str} -> {key_str}")
        
        print(f"✅ Key conversion successful: {key_objects}")
        
        # Test hotkey string creation
        hotkey_string = '+'.join(hotkey)
        pynput_format = '<' + '>+<'.join(hotkey) + '>'
        print(f"✅ Hotkey string: {hotkey_string}")
        print(f"✅ Pynput format: {pynput_format}")
        
        return True
        
    except ImportError as e:
        print(f"❌ pynput import failed: {e}")
        print("Install with: pip install pynput")
        return False
    except Exception as e:
        print(f"❌ Error testing hotkey: {e}")
        return False

def main():
    """Main test function"""
    print("Testing hotkey configuration...")
    
    if test_hotkey_config():
        print("\n🎉 Hotkey configuration test passed!")
        print("\nYou can now test the voice task manager:")
        print("python voice_task_manager.py")
    else:
        print("\n❌ Hotkey configuration test failed!")
        print("Please check the errors above.")

if __name__ == "__main__":
    main()
