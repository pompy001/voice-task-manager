"""
Speech-to-Text module using Faster-Whisper for Voice-Activated Task Manager
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any
import time

try:
    from faster_whisper import WhisperModel
except ImportError:
    print("Warning: faster-whisper not installed. Install with: pip install faster-whisper")
    WhisperModel = None

from config import STT_CONFIG

logger = logging.getLogger(__name__)

class SpeechToText:
    """Handles speech-to-text conversion using Faster-Whisper"""
    
    def __init__(self, model_size: str = None, device: str = None):
        """
        Initialize the STT model
        
        Args:
            model_size: Model size (tiny, base, small, medium, large)
            device: Device to use (cpu, cuda)
        """
        self.model_size = model_size or STT_CONFIG['model_size']
        self.device = device or STT_CONFIG['device']
        self.compute_type = STT_CONFIG['compute_type']
        self.language = STT_CONFIG['language']
        
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the Whisper model"""
        try:
            if WhisperModel is None:
                raise ImportError("faster-whisper not available")
                
            logger.info(f"Loading Whisper model: {self.model_size} on {self.device}")
            self.model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type
            )
            logger.info("Whisper model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            self.model = None
    
    def transcribe_audio(self, audio_file: str) -> Dict[str, Any]:
        """
        Transcribe audio file to text
        
        Args:
            audio_file: Path to the audio file
            
        Returns:
            Dictionary containing transcription results
        """
        if not self.model:
            return {
                'success': False,
                'error': 'Whisper model not loaded',
                'text': '',
                'confidence': 0.0
            }
        
        if not Path(audio_file).exists():
            return {
                'success': False,
                'error': f'Audio file not found: {audio_file}',
                'text': '',
                'confidence': 0.0
            }
        
        try:
            logger.info(f"Transcribing audio file: {audio_file}")
            start_time = time.time()
            
            # Transcribe audio
            segments, info = self.model.transcribe(
                audio_file,
                language=self.language,
                beam_size=5,
                best_of=5
            )
            
            # Collect all segments
            transcribed_text = ""
            total_confidence = 0.0
            segment_count = 0
            
            for segment in segments:
                transcribed_text += segment.text + " "
                total_confidence += segment.avg_logprob
                segment_count += 1
            
            # Calculate average confidence
            avg_confidence = total_confidence / segment_count if segment_count > 0 else 0.0
            
            # Convert log probability to confidence percentage (rough approximation)
            confidence_percentage = max(0, min(100, (avg_confidence + 1) * 50))
            
            transcription_time = time.time() - start_time
            
            result = {
                'success': True,
                'text': transcribed_text.strip(),
                'confidence': confidence_percentage,
                'language': info.language,
                'language_probability': info.language_probability,
                'transcription_time': transcription_time,
                'segment_count': segment_count
            }
            
            logger.info(f"Transcription completed in {transcription_time:.2f}s")
            logger.info(f"Text: {transcribed_text.strip()}")
            logger.info(f"Confidence: {confidence_percentage:.1f}%")
            
            return result
            
        except Exception as e:
            logger.error(f"Error during transcription: {e}")
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'confidence': 0.0
            }
    
    def transcribe_with_timestamps(self, audio_file: str) -> Dict[str, Any]:
        """
        Transcribe audio with detailed timestamps
        
        Args:
            audio_file: Path to the audio file
            
        Returns:
            Dictionary containing transcription with timestamps
        """
        if not self.model:
            return {
                'success': False,
                'error': 'Whisper model not loaded',
                'segments': [],
                'text': ''
            }
        
        try:
            logger.info(f"Transcribing audio with timestamps: {audio_file}")
            
            segments, info = self.model.transcribe(
                audio_file,
                language=self.language,
                beam_size=5,
                best_of=5,
                word_timestamps=True
            )
            
            # Collect segments with timestamps
            detailed_segments = []
            full_text = ""
            
            for segment in segments:
                segment_data = {
                    'start': segment.start,
                    'end': segment.end,
                    'text': segment.text,
                    'words': []
                }
                
                # Add word-level timestamps if available
                if hasattr(segment, 'words') and segment.words:
                    for word in segment.words:
                        word_data = {
                            'word': word.word,
                            'start': word.start,
                            'end': word.end,
                            'probability': word.probability
                        }
                        segment_data['words'].append(word_data)
                
                detailed_segments.append(segment_data)
                full_text += segment.text + " "
            
            result = {
                'success': True,
                'segments': detailed_segments,
                'text': full_text.strip(),
                'language': info.language,
                'language_probability': info.language_probability
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error during timestamped transcription: {e}")
            return {
                'success': False,
                'error': str(e),
                'segments': [],
                'text': ''
            }
    
    def is_available(self) -> bool:
        """Check if the STT system is available"""
        return self.model is not None
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        if not self.model:
            return {'loaded': False}
        
        return {
            'loaded': True,
            'model_size': self.model_size,
            'device': self.device,
            'compute_type': self.compute_type,
            'language': self.language
        }
    
    def cleanup(self):
        """Clean up resources"""
        # Faster-Whisper models are automatically cleaned up
        self.model = None
        logger.info("STT model cleaned up")


class MockSTT:
    """Mock STT for testing without actual model"""
    
    def __init__(self):
        self.mock_responses = [
            "please add a high priority task build a dashboard project given by sunny expected completed date 4 july",
            "what is the next priority task",
            "mark task number 3 as completed",
            "show me all urgent tasks"
        ]
        self.current_response = 0
    
    def transcribe_audio(self, audio_file: str) -> Dict[str, Any]:
        """Return mock transcription"""
        response = self.mock_responses[self.current_response % len(self.mock_responses)]
        self.current_response += 1
        
        return {
            'success': True,
            'text': response,
            'confidence': 95.0,
            'language': 'en',
            'language_probability': 0.99,
            'transcription_time': 0.5,
            'segment_count': 1
        }
    
    def is_available(self) -> bool:
        return True
    
    def cleanup(self):
        pass


if __name__ == "__main__":
    # Test STT functionality
    import logging
    logging.basicConfig(level=logging.INFO)
    
    # Test with mock STT if faster-whisper not available
    if WhisperModel is None:
        print("Using mock STT for testing")
        stt = MockSTT()
    else:
        stt = SpeechToText()
    
    try:
        # Test transcription
        result = stt.transcribe_audio("test_audio.wav")
        print(f"Transcription result: {result}")
        
        # Test model info
        info = stt.get_model_info()
        print(f"Model info: {info}")
        
    finally:
        stt.cleanup()

