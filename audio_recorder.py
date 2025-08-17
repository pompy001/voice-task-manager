"""
Audio recording module for Voice-Activated Task Manager
"""

import pyaudio
import numpy as np
import wave
import threading
import time
from pathlib import Path
from typing import Optional, Callable
import logging

from config import AUDIO_CONFIG, TEMP_DIR

logger = logging.getLogger(__name__)

class AudioRecorder:
    """Handles audio recording and processing"""
    
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.recording = False
        self.audio_data = []
        self.recording_thread = None
        self.silence_detector = SilenceDetector()
        
    def start_recording(self, duration: Optional[int] = None) -> str:
        """
        Start recording audio for the specified duration or until silence is detected
        
        Args:
            duration: Recording duration in seconds (None for silence-based)
            
        Returns:
            Path to the recorded audio file
        """
        if self.recording:
            logger.warning("Recording already in progress")
            return None
            
        self.recording = True
        self.audio_data = []
        
        # Create temporary file path
        timestamp = int(time.time())
        audio_file = TEMP_DIR / f"recording_{timestamp}.wav"
        
        # Start recording thread
        self.recording_thread = threading.Thread(
            target=self._record_audio,
            args=(audio_file, duration)
        )
        self.recording_thread.start()
        
        logger.info(f"Started recording to {audio_file}")
        return str(audio_file)
    
    def stop_recording(self):
        """Stop the current recording"""
        if not self.recording:
            return
            
        logger.info("Stopping recording...")
        self.recording = False
        
        # Wait for recording thread to complete
        if self.recording_thread and self.recording_thread.is_alive():
            logger.info("Waiting for recording thread to complete...")
            self.recording_thread.join(timeout=2.0)  # Wait up to 2 seconds
            
            if self.recording_thread.is_alive():
                logger.warning("Recording thread did not complete within timeout")
            else:
                logger.info("Recording thread completed successfully")
        
        self.recording_thread = None
        logger.info("Recording stopped")
    
    def _record_audio(self, output_file: Path, duration: Optional[int] = None):
        """Internal method to record audio"""
        try:
            stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=AUDIO_CONFIG['channels'],
                rate=AUDIO_CONFIG['sample_rate'],
                input=True,
                frames_per_buffer=AUDIO_CONFIG['chunk_size']
            )
            
            frames = []
            start_time = time.time()
            silence_start_time = None
            
            logger.info("Recording started - speak now!")
            
            while self.recording:
                try:
                    data = stream.read(AUDIO_CONFIG['chunk_size'])
                    frames.append(data)
                    
                    # Check if duration exceeded
                    if duration and (time.time() - start_time) >= duration:
                        logger.info(f"Recording stopped after {duration} seconds")
                        break
                    
                    # Check for silence (if no duration specified)
                    if not duration:
                        audio_chunk = np.frombuffer(data, dtype=np.int16)
                        if self.silence_detector.is_silence(audio_chunk):
                            if silence_start_time is None:
                                silence_start_time = time.time()
                                logger.info("Silence detected, waiting for confirmation...")
                            
                            # Check if we've had enough silence
                            silence_duration = time.time() - silence_start_time
                            if silence_duration >= 1.0:  # 1 second of silence
                                logger.info(f"Recording stopped after {silence_duration:.1f} seconds of silence")
                                break
                        else:
                            # Reset silence timer if we detect sound
                            silence_start_time = None
                    
                    # Small delay to allow for stop requests
                    time.sleep(0.01)
                                
                except Exception as e:
                    logger.error(f"Error reading audio data: {e}")
                    break
            
            stream.stop_stream()
            stream.close()
            
            # Save audio to file
            self._save_audio(frames, output_file)
            logger.info(f"Audio saved to {output_file}")
            
        except Exception as e:
            logger.error(f"Error in audio recording: {e}")
    
    def _save_audio(self, frames: list, output_file: Path):
        """Save recorded audio frames to WAV file"""
        try:
            with wave.open(str(output_file), 'wb') as wf:
                wf.setnchannels(AUDIO_CONFIG['channels'])
                wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
                wf.setframerate(AUDIO_CONFIG['sample_rate'])
                wf.writeframes(b''.join(frames))
        except Exception as e:
            logger.error(f"Error saving audio file: {e}")
    
    def is_recording(self) -> bool:
        """Check if currently recording"""
        return self.recording
    
    def cleanup(self):
        """Clean up audio resources"""
        if self.recording:
            self.stop_recording()
        self.audio.terminate()
        logger.info("Audio recorder cleaned up")


class SilenceDetector:
    """Detects silence in audio to automatically stop recording"""
    
    def __init__(self, threshold: float = None):
        self.threshold = threshold or AUDIO_CONFIG['silence_threshold']
        self.silence_frames = 0
        # Require 1 second of silence before stopping
        self.min_silence_frames = int(1.0 * AUDIO_CONFIG['sample_rate'] / AUDIO_CONFIG['chunk_size'])
        self.last_audio_level = 0
    
    def is_silence(self, audio_chunk: np.ndarray) -> bool:
        """
        Check if audio chunk represents silence
        
        Args:
            audio_chunk: Audio data as numpy array
            
        Returns:
            True if silence detected, False otherwise
        """
        # Calculate RMS (Root Mean Square) of audio chunk
        rms = np.sqrt(np.mean(audio_chunk.astype(np.float32) ** 2))
        
        # Normalize RMS to 0-1 range
        normalized_rms = rms / 32768.0  # Max value for int16
        
        # Update last audio level for comparison
        self.last_audio_level = normalized_rms
        
        if normalized_rms < self.threshold:
            self.silence_frames += 1
        else:
            # Reset silence counter if we detect sound
            self.silence_frames = 0
        
        # Log audio levels for debugging
        if self.silence_frames % 10 == 0:  # Log every 10 frames
            logger.debug(f"Audio level: {normalized_rms:.4f}, Silence frames: {self.silence_frames}")
        
        return self.silence_frames >= self.min_silence_frames


class AudioPlayer:
    """Simple audio player for playing back TTS responses"""
    
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self._check_output_devices()
        # Use a specific working speaker device instead of default
        self.preferred_device = self._find_preferred_device()
    
    def _find_preferred_device(self):
        """Find the best speaker device to use (cross-platform)"""
        try:
            # First, check if we have a saved working device
            try:
                if Path("working_audio_device.txt").exists():
                    with open("working_audio_device.txt", "r") as f:
                        saved_device = int(f.read().strip())
                        logger.info(f"Using saved working device: {saved_device}")
                        return saved_device
            except:
                pass
            
            # Cross-platform speaker device detection
            import platform
            system = platform.system().lower()
            
            if system == "darwin":  # macOS
                # On macOS, look for built-in speakers or external speakers
                for i in range(self.audio.get_device_count()):
                    device_info = self.audio.get_device_info_by_index(i)
                    if (device_info['maxOutputChannels'] > 0 and 
                        ('speaker' in device_info['name'].lower() or 
                         'output' in device_info['name'].lower() or
                         'built-in' in device_info['name'].lower())):
                        logger.info(f"Found macOS speaker device: {device_info['name']} (index {i})")
                        return i
                        
            elif system == "windows":
                # On Windows, look for Realtek speakers first (usually the main speakers)
                for i in range(self.audio.get_device_count()):
                    device_info = self.audio.get_device_info_by_index(i)
                    if (device_info['maxOutputChannels'] > 0 and 
                        'realtek' in device_info['name'].lower() and 
                        'speaker' in device_info['name'].lower()):
                        logger.info(f"Found preferred Windows speaker device: {device_info['name']} (index {i})")
                        return i
                
                # Fallback to any speaker device on Windows
                for i in range(self.audio.get_device_count()):
                    device_info = self.audio.get_device_info_by_index(i)
                    if (device_info['maxOutputChannels'] > 0 and 
                        'speaker' in device_info['name'].lower()):
                        logger.info(f"Found fallback Windows speaker device: {device_info['name']} (index {i})")
                        return i
            else:
                # Linux and other systems - look for any speaker device
                for i in range(self.audio.get_device_count()):
                    device_info = self.audio.get_device_info_by_index(i)
                    if (device_info['maxOutputChannels'] > 0 and 
                        'speaker' in device_info['name'].lower()):
                        logger.info(f"Found speaker device: {device_info['name']} (index {i})")
                        return i
            
            # If no specific speakers found, use default
            logger.warning("No preferred speaker device found, using default")
            return None
            
        except Exception as e:
            logger.error(f"Error finding preferred device: {e}")
            return None
    
    def _check_output_devices(self):
        """Check available output devices"""
        try:
            output_devices = []
            for i in range(self.audio.get_device_count()):
                device_info = self.audio.get_device_info_by_index(i)
                if device_info['maxOutputChannels'] > 0:
                    output_devices.append({
                        'index': i,
                        'name': device_info['name'],
                        'channels': device_info['maxOutputChannels']
                    })
            
            if output_devices:
                logger.info(f"Found {len(output_devices)} output devices")
                for device in output_devices:
                    logger.info(f"  Device {device['index']}: {device['name']} ({device['channels']} channels)")
            else:
                logger.warning("No output devices found")
                
        except Exception as e:
            logger.error(f"Error checking output devices: {e}")
    
    def play_audio(self, audio_file: str):
        """
        Play an audio file
        
        Args:
            audio_file: Path to the audio file to play
        """
        try:
            logger.info(f"Attempting to play audio: {audio_file}")
            
            # Check if file exists
            if not Path(audio_file).exists():
                logger.error(f"Audio file not found: {audio_file}")
                return
            
            with wave.open(audio_file, 'rb') as wf:
                logger.info(f"Audio file info: {wf.getnchannels()} channels, {wf.getframerate()} Hz, {wf.getsampwidth()} bytes")
                
                # Try to open output stream with preferred device
                try:
                    if self.preferred_device is not None:
                        logger.info(f"Using preferred device: {self.preferred_device}")
                        stream = self.audio.open(
                            format=self.audio.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),
                            output=True,
                            output_device_index=self.preferred_device
                        )
                    else:
                        logger.info("Using default output device")
                        stream = self.audio.open(
                            format=self.audio.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),
                            output=True
                        )
                    
                    logger.info("Audio output stream opened successfully")
                    
                except Exception as e:
                    logger.error(f"Failed to open audio output stream: {e}")
                    logger.error("This usually means no default output device is available")
                    return
                
                # Play the audio
                try:
                    data = wf.readframes(AUDIO_CONFIG['chunk_size'])
                    frames_played = 0
                    
                    while data:
                        stream.write(data)
                        data = wf.readframes(AUDIO_CONFIG['chunk_size'])
                        frames_played += 1
                    
                    logger.info(f"Audio playback completed: {frames_played} frames played")
                    
                except Exception as e:
                    logger.error(f"Error during audio playback: {e}")
                finally:
                    stream.stop_stream()
                    stream.close()
                    logger.info("Audio stream closed")
                
        except Exception as e:
            logger.error(f"Error playing audio: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    def cleanup(self):
        """Clean up audio player resources"""
        try:
            self.audio.terminate()
            logger.info("Audio player cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up audio player: {e}")


if __name__ == "__main__":
    # Test audio recording
    import logging
    logging.basicConfig(level=logging.INFO)
    
    recorder = AudioRecorder()
    player = AudioPlayer()
    
    try:
        print("Starting 5-second recording test...")
        audio_file = recorder.start_recording(duration=5)
        time.sleep(6)  # Wait for recording to complete
        
        print(f"Recording saved to: {audio_file}")
        print("Playing back recording...")
        player.play_audio(audio_file)
        
    finally:
        recorder.cleanup()
        player.cleanup()

