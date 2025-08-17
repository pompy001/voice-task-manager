#!/usr/bin/env python3
"""
Simple TTS Installation Script
Installs pyttsx3 (no Hugging Face dependencies) for the voice task manager
"""

import subprocess
import sys
import platform

def install_pyttsx3():
    """Install pyttsx3 TTS library"""
    print("🎤 Installing PyTTSX3 TTS (No Hugging Face Dependencies)")
    print("=" * 60)
    
    try:
        # Install pyttsx3
        print("📦 Installing pyttsx3...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "pyttsx3>=2.90"
        ], capture_output=True, text=True, check=True)
        
        print("✅ pyttsx3 installed successfully!")
        
        # Test the installation
        print("\n🧪 Testing pyttsx3 installation...")
        test_result = subprocess.run([
            sys.executable, "-c", 
            "import pyttsx3; engine = pyttsx3.init(); voices = engine.getProperty('voices'); print(f'Found {len(voices)} voices'); engine.stop()"
        ], capture_output=True, text=True)
        
        if test_result.returncode == 0:
            print("✅ pyttsx3 is working correctly!")
            print(test_result.stdout.strip())
        else:
            print("⚠️  pyttsx3 installed but may have issues")
            print(test_result.stderr.strip())
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install pyttsx3: {e}")
        print("Error output:", e.stderr)
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    return True

def test_tts_system():
    """Test the complete TTS system"""
    print("\n🔊 Testing Complete TTS System")
    print("=" * 40)
    
    try:
        # Test the new TTS implementation
        from text_to_speech_pyttsx3 import TextToSpeech
        
        tts = TextToSpeech()
        
        if tts.is_available():
            print("✅ TTS system is available")
            
            # List voices
            voices = tts.list_voices()
            if voices:
                print(f"🎵 Found {len(voices)} voices:")
                for voice in voices:
                    print(f"  - {voice['name']}")
            
            # Test speech generation
            print("\n🔊 Testing speech generation...")
            result = tts.generate_speech("Hello! This is a test of the new TTS system.")
            
            if result['success']:
                print(f"✅ Speech generated: {result['output_file']}")
                print(f"📊 Duration: {result['audio_duration']:.1f} seconds")
                
                # Test playback
                print("\n🎵 Testing audio playback...")
                from audio_recorder import AudioPlayer
                player = AudioPlayer()
                player.play_audio(result['output_file'])
                player.cleanup()
                
                print("✅ Audio playback test completed!")
            else:
                print(f"❌ Speech generation failed: {result.get('error')}")
            
            tts.cleanup()
            
        else:
            print("❌ TTS system is not available")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all dependencies are installed")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def main():
    """Main installation function"""
    print("🚀 Voice Task Manager - Simple TTS Installation")
    print("=" * 60)
    
    system = platform.system()
    print(f"Detected OS: {system}")
    
    # Install pyttsx3
    if not install_pyttsx3():
        print("\n❌ Installation failed!")
        return
    
    # Test the system
    if test_tts_system():
        print("\n🎉 TTS installation and testing completed successfully!")
        print("\n💡 You can now use the voice task manager with the new TTS system!")
        print("   Run: python test_pyttsx3_tts.py")
        print("   Or: python voice_task_manager_universal.py")
    else:
        print("\n⚠️  Installation completed but testing failed")
        print("   Check the error messages above for troubleshooting")

if __name__ == "__main__":
    main()
