#!/usr/bin/env python3
"""
Quick test script to verify all components are working
"""

import sys
import os

def test_import(module_name, description):
    """Test if a module can be imported"""
    try:
        __import__(module_name)
        print(f"✅ {description} - OK")
        return True
    except ImportError as e:
        print(f"❌ {description} - FAILED: {e}")
        return False

def test_openai():
    """Test OpenAI client"""
    try:
        from openai_client import OpenAIClient, MockOpenAIClient
        print("✅ OpenAI Client - OK")
        return True
    except Exception as e:
        print(f"❌ OpenAI Client - FAILED: {e}")
        return False

def test_audio():
    """Test audio components"""
    try:
        import pyaudio
        p = pyaudio.PyAudio()
        device_count = p.get_device_count()
        p.terminate()
        print(f"✅ PyAudio - OK (Found {device_count} audio devices)")
        return True
    except Exception as e:
        print(f"❌ PyAudio - FAILED: {e}")
        return False

def test_config():
    """Test configuration"""
    try:
        from config import HOTKEY_COMBO, AUDIO_CONFIG
        print("✅ Configuration - OK")
        return True
    except Exception as e:
        print(f"❌ Configuration - FAILED: {e}")
        return False

def main():
    """Run all tests"""
    print("="*60)
    print("Voice Task Manager - Component Test")
    print("="*60)
    
    all_good = True
    
    # Test core Python modules
    print("\n🔍 Testing Core Components:")
    all_good &= test_import("pynput", "Global Hotkey Detection")
    all_good &= test_import("openpyxl", "Excel Integration")
    all_good &= test_import("requests", "HTTP Requests")
    all_good &= test_import("soundfile", "Audio File Handling")
    all_good &= test_import("dotenv", "Environment Variables")
    
    # Test audio
    print("\n🔊 Testing Audio Components:")
    all_good &= test_audio()
    
    # Test AI components
    print("\n🤖 Testing AI Components:")
    all_good &= test_openai()
    
    # Test configuration
    print("\n⚙️  Testing Configuration:")
    all_good &= test_config()
    
    # Test optional components
    print("\n📦 Testing Optional Components:")
    try:
        from faster_whisper import WhisperModel
        print("✅ Faster Whisper - OK")
    except ImportError:
        print("⚠️  Faster Whisper - Not installed (will use mock)")
    
    try:
        from kittentts import KittenTTS
        print("✅ KittenTTS - OK")
    except ImportError:
        print("⚠️  KittenTTS - Not installed (will use mock)")
    
    # Summary
    print("\n" + "="*60)
    if all_good:
        print("🎉 All core components are working!")
        print("\nNext steps:")
        print("1. Set up OpenAI API key: python configure_api.py")
        print("2. Test the system: python test_system.py")
        print("3. Run voice task manager: python voice_task_manager.py")
    else:
        print("⚠️  Some components have issues.")
        print("Please check the errors above and install missing dependencies.")
        print("\nTry: pip install -r requirements.txt")
    
    print("="*60)

if __name__ == "__main__":
    main()
