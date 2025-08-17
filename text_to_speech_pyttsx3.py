#!/usr/bin/env python3
"""
Text-to-Speech using pyttsx3 (No Hugging Face dependencies)
Cross-platform TTS with system voices
"""

import os
import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import tempfile

logger = logging.getLogger(__name__)

# Create temp directory
TEMP_DIR = Path.home() / '.voice_task_manager' / 'temp'
TEMP_DIR.mkdir(parents=True, exist_ok=True)

class PyTTSX3TTS:
    """Text-to-Speech using pyttsx3 (system voices)"""
    
    def __init__(self):
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
            self._configure_engine()
            self.available = True
            logger.info("PyTTSX3 TTS initialized successfully")
        except ImportError:
            logger.error("pyttsx3 not available - install with: pip install pyttsx3")
            self.available = False
        except Exception as e:
            logger.error(f"Error initializing PyTTSX3: {e}")
            self.available = False
    
    def _configure_engine(self):
        """Configure the TTS engine"""
        try:
            # Get available voices
            voices = self.engine.getProperty('voices')
            logger.info(f"Found {len(voices)} available voices")
            
            # Set default voice (usually the first one)
            if voices:
                self.engine.setProperty('voice', voices[0].id)
                logger.info(f"Using voice: {voices[0].name}")
            
            # Set speech rate (words per minute)
            self.engine.setProperty('rate', 150)  # Default is usually 200
            
            # Set volume (0.0 to 1.0)
            self.engine.setProperty('volume', 0.9)
            
        except Exception as e:
            logger.error(f"Error configuring TTS engine: {e}")
    
    def generate_speech(self, text: str, voice: str = None, output_file: str = None) -> Dict[str, Any]:
        """Generate speech from text"""
        if not self.available:
            return {
                'success': False,
                'error': 'PyTTSX3 not available'
            }
        
        try:
            # Create output file path
            if not output_file:
                timestamp = int(time.time())
                output_file = str(TEMP_DIR / f"pyttsx3_tts_{timestamp}.wav")
            
            # Set voice if specified
            if voice:
                self._set_voice(voice)
            
            # Generate speech and save to file
            self.engine.save_to_file(text, output_file)
            self.engine.runAndWait()
            
            # Check if file was created
            if Path(output_file).exists():
                file_size = Path(output_file).stat().st_size
                logger.info(f"Speech generated: {output_file} ({file_size} bytes)")
                
                return {
                    'success': True,
                    'output_file': output_file,
                    'text': text,
                    'voice': voice or 'system-default',
                    'sample_rate': 22050,  # pyttsx3 default
                    'generation_time': 0.1,
                    'audio_duration': len(text.split()) / 2.5  # Rough estimate
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to create audio file'
                }
                
        except Exception as e:
            logger.error(f"Error generating speech: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _set_voice(self, voice_name: str):
        """Set a specific voice by name"""
        try:
            voices = self.engine.getProperty('voices')
            for voice in voices:
                if voice_name.lower() in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    logger.info(f"Set voice to: {voice.name}")
                    return True
            
            logger.warning(f"Voice '{voice_name}' not found, using default")
            return False
            
        except Exception as e:
            logger.error(f"Error setting voice: {e}")
            return False
    
    def speak(self, text: str) -> Dict[str, Any]:
        """Speak text directly (alias for generate_speech)"""
        return self.generate_speech(text)
    
    def is_available(self) -> bool:
        """Check if TTS is available"""
        return self.available
    
    def list_voices(self) -> list:
        """List available voices"""
        if not self.available:
            return []
        
        try:
            voices = self.engine.getProperty('voices')
            voice_list = []
            for i, voice in enumerate(voices):
                voice_list.append({
                    'id': i,
                    'name': voice.name,
                    'languages': getattr(voice, 'languages', []),
                    'gender': getattr(voice, 'gender', 'unknown')
                })
            return voice_list
        except Exception as e:
            logger.error(f"Error listing voices: {e}")
            return []
    
    def cleanup(self):
        """Clean up TTS resources"""
        try:
            if hasattr(self, 'engine'):
                self.engine.stop()
                logger.info("PyTTSX3 TTS cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up PyTTSX3: {e}")

class TTSManager:
    """TTS Manager with caching and fallback"""
    
    def __init__(self):
        self.tts = PyTTSX3TTS()
        self.cache = {}
        self.cache_dir = TEMP_DIR / 'tts_cache'
        self.cache_dir.mkdir(exist_ok=True)
    
    def speak(self, text: str, voice: str = None) -> Dict[str, Any]:
        """Generate speech with caching"""
        # Check cache first
        cache_key = f"{text}_{voice}"
        if cache_key in self.cache:
            logger.info("Using cached TTS result")
            return self.cache[cache_key]
        
        # Generate new speech
        result = self.tts.generate_speech(text, voice)
        
        # Cache the result
        if result['success']:
            self.cache[cache_key] = result
        
        return result
    
    def generate_speech(self, text: str, voice: str = None) -> Dict[str, Any]:
        """Alias for speak method"""
        return self.speak(text, voice)
    
    def is_available(self) -> bool:
        """Check if TTS is available"""
        return self.tts.is_available()
    
    def list_voices(self) -> list:
        """List available voices"""
        return self.tts.list_voices()
    
    def cleanup(self):
        """Clean up TTS resources"""
        self.tts.cleanup()

class MockTTS:
    """Mock TTS for testing (keeps existing functionality)"""
    
    def __init__(self):
        self.mock_audio = None
    
    def generate_speech(self, text: str, voice: str = None, output_file: str = None) -> Dict[str, Any]:
        """Return mock TTS result"""
        if not output_file:
            timestamp = int(time.time())
            output_file = str(TEMP_DIR / f"mock_tts_{timestamp}.wav")
        
        # Create a LOUD mock audio file (multiple frequencies, higher volume)
        import numpy as np
        
        # Generate 3 seconds of audio at 24kHz
        sample_rate = 24000
        duration = 3.0
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Create multiple frequencies for better audibility
        freq1 = 440   # A4 note
        freq2 = 880   # A5 note
        freq3 = 1760  # A6 note
        
        # Generate tones and make them LOUD
        audio1 = np.sin(2 * np.pi * freq1 * t) * 0.6
        audio2 = np.sin(2 * np.pi * freq2 * t) * 0.4
        audio3 = np.sin(2 * np.pi * freq3 * t) * 0.3
        
        # Combine and make it very loud
        mock_audio = (audio1 + audio2 + audio3) * 0.9  # High volume
        
        try:
            import soundfile as sf
            sf.write(output_file, mock_audio, sample_rate)
            return {
                'success': True,
                'output_file': output_file,
                'text': text,
                'voice': voice or 'mock-voice',
                'sample_rate': sample_rate,
                'generation_time': 0.1,
                'audio_duration': duration
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'output_file': None
            }
    
    def is_available(self) -> bool:
        return True
    
    def cleanup(self):
        pass

# Main TTS class for backward compatibility
class TextToSpeech:
    """Main TTS class that automatically selects the best available TTS engine"""
    
    def __init__(self):
        # Try PyTTSX3 first
        self.tts = PyTTSX3TTS()
        
        if not self.tts.is_available():
            # Fallback to MockTTS
            logger.warning("PyTTSX3 not available, using MockTTS")
            self.tts = MockTTS()
    
    def generate_speech(self, text: str, voice: str = None) -> Dict[str, Any]:
        """Generate speech using the best available TTS engine"""
        return self.tts.generate_speech(text, voice)
    
    def speak(self, text: str, voice: str = None) -> Dict[str, Any]:
        """Alias for generate_speech"""
        return self.generate_speech(text, voice)
    
    def is_available(self) -> bool:
        """Check if TTS is available"""
        return self.tts.is_available()
    
    def list_voices(self) -> list:
        """List available voices (if supported)"""
        if hasattr(self.tts, 'list_voices'):
            return self.tts.list_voices()
        return []
    
    def cleanup(self):
        """Clean up TTS resources"""
        self.tts.cleanup()

if __name__ == "__main__":
    # Test the TTS system
    logging.basicConfig(level=logging.INFO)
    
    print("🎤 Testing PyTTSX3 TTS System")
    print("=" * 40)
    
    tts = TextToSpeech()
    
    if tts.is_available():
        print("✅ TTS system is available")
        
        # List available voices
        voices = tts.list_voices()
        if voices:
            print(f"\n🎵 Available voices ({len(voices)}):")
            for voice in voices:
                print(f"  - {voice['name']} ({voice.get('gender', 'unknown')})")
        
        # Test speech generation
        test_text = "Hello! This is a test of the PyTTSX3 text-to-speech system."
        print(f"\n🔊 Testing speech generation: '{test_text}'")
        
        result = tts.generate_speech(test_text)
        if result['success']:
            print(f"✅ Speech generated successfully: {result['output_file']}")
            print(f"📊 Duration: {result['audio_duration']:.1f} seconds")
        else:
            print(f"❌ Speech generation failed: {result.get('error')}")
    else:
        print("❌ TTS system is not available")
    
    tts.cleanup()
