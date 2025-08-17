"""
Text-to-Speech module using KittenTTS for Voice-Activated Task Manager
"""

import logging
import soundfile as sf
from pathlib import Path
from typing import Optional, Dict, Any, List
import time
import threading

try:
    from kittentts import KittenTTS
except ImportError:
    print("Warning: KittenTTS not installed. Install with: pip install https://github.com/KittenML/KittenTTS/releases/download/0.1/kittentts-0.1.0-py3-none-any.whl")
    KittenTTS = None

from config import TTS_CONFIG, TEMP_DIR

logger = logging.getLogger(__name__)

class TextToSpeech:
    """Handles text-to-speech conversion using KittenTTS"""
    
    def __init__(self, model: str = None, voice: str = None):
        """
        Initialize the TTS system
        
        Args:
            model: KittenTTS model to use
            voice: Voice to use for speech synthesis
        """
        self.model_name = model or TTS_CONFIG['model']
        self.voice = voice or TTS_CONFIG['voice']
        self.sample_rate = TTS_CONFIG['sample_rate']
        
        self.model = None
        self.available_voices = [
            'expr-voice-2-m', 'expr-voice-2-f', 
            'expr-voice-3-m', 'expr-voice-3-f',
            'expr-voice-4-m', 'expr-voice-4-f', 
            'expr-voice-5-m', 'expr-voice-5-f'
        ]
        
        self._load_model()
    
    def _load_model(self):
        """Load the KittenTTS model"""
        try:
            if KittenTTS is None:
                raise ImportError("KittenTTS not available")
            
            logger.info(f"Loading KittenTTS model: {self.model_name}")
            self.model = KittenTTS(self.model_name)
            logger.info("KittenTTS model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load KittenTTS model: {e}")
            self.model = None
    
    def generate_speech(self, text: str, voice: str = None, output_file: str = None) -> Dict[str, Any]:
        """
        Generate speech from text
        
        Args:
            text: Text to convert to speech
            voice: Voice to use (overrides default)
            output_file: Output file path (auto-generated if None)
            
        Returns:
            Dictionary containing generation results
        """
        if not self.model:
            return {
                'success': False,
                'error': 'KittenTTS model not loaded',
                'output_file': None
            }
        
        if not text or not text.strip():
            return {
                'success': False,
                'error': 'No text provided',
                'output_file': None
            }
        
        # Use specified voice or default
        selected_voice = voice or self.voice
        
        # Validate voice
        if selected_voice not in self.available_voices:
            logger.warning(f"Invalid voice '{selected_voice}', using default '{self.voice}'")
            selected_voice = self.voice
        
        try:
            logger.info(f"Generating speech for text: '{text[:50]}...' with voice: {selected_voice}")
            start_time = time.time()
            
            # Generate audio
            audio = self.model.generate(text, voice=selected_voice)
            
            # Generate output filename if not provided
            if not output_file:
                timestamp = int(time.time())
                output_file = str(TEMP_DIR / f"tts_output_{timestamp}.wav")
            
            # Save audio to file
            sf.write(output_file, audio, self.sample_rate)
            
            generation_time = time.time() - start_time
            
            result = {
                'success': True,
                'output_file': output_file,
                'text': text,
                'voice': selected_voice,
                'sample_rate': self.sample_rate,
                'generation_time': generation_time,
                'audio_duration': len(audio) / self.sample_rate
            }
            
            logger.info(f"Speech generated in {generation_time:.2f}s, saved to: {output_file}")
            return result
            
        except Exception as e:
            logger.error(f"Error generating speech: {e}")
            return {
                'success': False,
                'error': str(e),
                'output_file': None
            }
    
    def generate_speech_async(self, text: str, voice: str = None, callback: callable = None) -> threading.Thread:
        """
        Generate speech asynchronously
        
        Args:
            text: Text to convert to speech
            voice: Voice to use
            callback: Function to call when generation is complete
            
        Returns:
            Thread object running the generation
        """
        def _generate():
            result = self.generate_speech(text, voice)
            if callback:
                callback(result)
        
        thread = threading.Thread(target=_generate)
        thread.start()
        return thread
    
    def batch_generate(self, texts: List[str], voice: str = None) -> List[Dict[str, Any]]:
        """
        Generate speech for multiple texts
        
        Args:
            texts: List of texts to convert
            voice: Voice to use for all generations
            
        Returns:
            List of generation results
        """
        results = []
        
        for i, text in enumerate(texts):
            logger.info(f"Generating speech {i+1}/{len(texts)}")
            result = self.generate_speech(text, voice)
            results.append(result)
            
            # Small delay between generations to avoid overwhelming the system
            if i < len(texts) - 1:
                time.sleep(0.1)
        
        return results
    
    def get_available_voices(self) -> List[str]:
        """Get list of available voices"""
        return self.available_voices.copy()
    
    def set_voice(self, voice: str) -> bool:
        """
        Set the default voice
        
        Args:
            voice: Voice to set as default
            
        Returns:
            True if voice was set successfully, False otherwise
        """
        if voice in self.available_voices:
            self.voice = voice
            logger.info(f"Default voice set to: {voice}")
            return True
        else:
            logger.warning(f"Invalid voice: {voice}. Available voices: {self.available_voices}")
            return False
    
    def is_available(self) -> bool:
        """Check if the TTS system is available"""
        return self.model is not None
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        if not self.model:
            return {'loaded': False}
        
        return {
            'loaded': True,
            'model': self.model_name,
            'voice': self.voice,
            'sample_rate': self.sample_rate,
            'available_voices': self.available_voices
        }
    
    def cleanup(self):
        """Clean up resources"""
        # KittenTTS models are automatically cleaned up
        self.model = None
        logger.info("TTS model cleaned up")


class MockTTS:
    """Mock TTS for testing without actual model"""
    
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


class TTSManager:
    """High-level TTS manager with caching and optimization"""
    
    def __init__(self, model: str = None, voice: str = None):
        """
        Initialize TTS manager
        
        Args:
            model: KittenTTS model to use
            voice: Default voice to use
        """
        self.tts = TextToSpeech(model, voice)
        self.cache = {}
        self.cache_size = 100  # Maximum number of cached items
        
    def speak(self, text: str, voice: str = None, cache: bool = True) -> Dict[str, Any]:
        """
        Convert text to speech with optional caching
        
        Args:
            text: Text to convert
            voice: Voice to use
            cache: Whether to cache the result
            
        Returns:
            Generation result
        """
        # Check cache first
        cache_key = f"{text}_{voice or self.tts.voice}"
        if cache and cache_key in self.cache:
            logger.info(f"Using cached TTS for: {text[:30]}...")
            return self.cache[cache_key]
        
        # Generate speech
        result = self.tts.generate_speech(text, voice)
        
        # Cache result if successful
        if cache and result['success']:
            self._add_to_cache(cache_key, result)
        
        return result
    
    def speak_async(self, text: str, voice: str = None, callback: callable = None):
        """Speak text asynchronously"""
        return self.tts.generate_speech_async(text, voice, callback)
    
    def generate_speech(self, text: str, voice: str = None, output_file: str = None) -> Dict[str, Any]:
        """
        Generate speech (alias for speak method for compatibility)
        
        Args:
            text: Text to convert
            voice: Voice to use
            output_file: Output file path (ignored, kept for compatibility)
            
        Returns:
            Generation result
        """
        return self.speak(text, voice)
    
    def _add_to_cache(self, key: str, result: Dict[str, Any]):
        """Add result to cache with size management"""
        if len(self.cache) >= self.cache_size:
            # Remove oldest item
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        self.cache[key] = result
    
    def clear_cache(self):
        """Clear the TTS cache"""
        self.cache.clear()
        logger.info("TTS cache cleared")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get cache information"""
        return {
            'size': len(self.cache),
            'max_size': self.cache_size,
            'keys': list(self.cache.keys())
        }
    
    def is_available(self) -> bool:
        """Check if TTS is available"""
        return self.tts.is_available()
    
    def cleanup(self):
        """Clean up TTS manager"""
        self.tts.cleanup()
        self.clear_cache()


if __name__ == "__main__":
    # Test TTS functionality
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Test with mock TTS if KittenTTS not available
    if KittenTTS is None:
        print("Using mock TTS for testing")
        tts = MockTTS()
    else:
        tts = TextToSpeech()
    
    try:
        # Test speech generation
        test_text = "Hello, this is a test of the text to speech system."
        result = tts.generate_speech(test_text)
        print(f"TTS result: {result}")
        
        # Test model info
        info = tts.get_model_info()
        print(f"Model info: {info}")
        
        # Test available voices
        if hasattr(tts, 'get_available_voices'):
            voices = tts.get_available_voices()
            print(f"Available voices: {voices}")
        
    finally:
        tts.cleanup()

