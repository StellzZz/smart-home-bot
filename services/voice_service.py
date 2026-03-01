"""Voice recognition and synthesis service"""

import asyncio
import io
import tempfile
import os
from typing import Optional, Dict, Any
from datetime import datetime

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False

try:
    import pyttsx3
    SPEECH_SYNTHESIS_AVAILABLE = True
except ImportError:
    SPEECH_SYNTHESIS_AVAILABLE = False

from config.settings import settings
from config.logging_config import logger
from utils.validators import NaturalLanguageProcessor


class VoiceService:
    """Service for voice recognition and synthesis"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer() if SPEECH_RECOGNITION_AVAILABLE else None
        self.microphone = None
        self.synthesis_engine = None
        self.nlp_processor = NaturalLanguageProcessor()
        
        if SPEECH_RECOGNITION_AVAILABLE:
            try:
                # Initialize microphone
                self.microphone = sr.Microphone()
                
                # Calibrate recognizer for ambient noise
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                logger.info("Voice recognition initialized")
            except Exception as e:
                logger.error(f"Error initializing voice recognition: {e}")
                self.recognizer = None
        
        if SPEECH_SYNTHESIS_AVAILABLE and settings.SPEECH_SYNTHESIS_ENABLED:
            try:
                self.synthesis_engine = pyttsx3.init()
                
                # Configure voice properties
                voices = self.synthesis_engine.getProperty('voices')
                if voices:
                    # Try to find Russian voice
                    for voice in voices:
                        if 'ru' in voice.id.lower() or 'russian' in voice.name.lower():
                            self.synthesis_engine.setProperty('voice', voice.id)
                            break
                
                # Set speech rate and volume
                self.synthesis_engine.setProperty('rate', 150)
                self.synthesis_engine.setProperty('volume', 0.9)
                
                logger.info("Speech synthesis initialized")
            except Exception as e:
                logger.error(f"Error initializing speech synthesis: {e}")
                self.synthesis_engine = None
    
    async def recognize_from_file(self, audio_file_path: str) -> Optional[str]:
        """Recognize speech from audio file"""
        if not self.recognizer or not SPEECH_RECOGNITION_AVAILABLE:
            logger.warning("Speech recognition not available")
            return None
        
        try:
            with sr.AudioFile(audio_file_path) as source:
                audio = self.recognizer.record(source)
            
            # Recognize speech using Google Speech Recognition
            text = self.recognizer.recognize_google(
                audio, 
                language=settings.SPEECH_LANGUAGE
            )
            
            logger.info(f"Speech recognized: {text}")
            return text
            
        except sr.UnknownValueError:
            logger.warning("Google Speech Recognition could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"Could not request results from Google Speech Recognition: {e}")
            return None
        except Exception as e:
            logger.error(f"Error in speech recognition: {e}")
            return None
    
    async def recognize_from_bytes(self, audio_data: bytes) -> Optional[str]:
        """Recognize speech from audio bytes"""
        if not self.recognizer or not SPEECH_RECOGNITION_AVAILABLE:
            logger.warning("Speech recognition not available")
            return None
        
        try:
            # Create audio data from bytes
            audio = sr.AudioData(audio_data, 16000, 2)  # Sample rate, channels
            
            # Recognize speech
            text = self.recognizer.recognize_google(
                audio,
                language=settings.SPEECH_LANGUAGE
            )
            
            logger.info(f"Speech recognized from bytes: {text}")
            return text
            
        except Exception as e:
            logger.error(f"Error in speech recognition from bytes: {e}")
            return None
    
    async def listen_microphone(self, timeout: int = 5) -> Optional[str]:
        """Listen from microphone and recognize speech"""
        if not self.microphone or not self.recognizer:
            logger.warning("Microphone not available")
            return None
        
        try:
            with self.microphone as source:
                logger.info("Listening...")
                audio = self.recognizer.listen(source, timeout=timeout)
            
            # Recognize speech
            text = self.recognizer.recognize_google(
                audio,
                language=settings.SPEECH_LANGUAGE
            )
            
            logger.info(f"Speech recognized from microphone: {text}")
            return text
            
        except sr.WaitTimeoutError:
            logger.warning("Listening timeout")
            return None
        except sr.UnknownValueError:
            logger.warning("Could not understand audio")
            return None
        except Exception as e:
            logger.error(f"Error listening from microphone: {e}")
            return None
    
    async def synthesize_speech(self, text: str, save_to_file: bool = False) -> Optional[bytes]:
        """Synthesize speech from text"""
        if not self.synthesis_engine or not SPEECH_SYNTHESIS_AVAILABLE:
            logger.warning("Speech synthesis not available")
            return None
        
        try:
            if save_to_file:
                # Save to temporary file
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                    temp_filename = temp_file.name
                
                self.synthesis_engine.save_to_file(text, temp_filename)
                self.synthesis_engine.runAndWait()
                
                # Read file and return bytes
                with open(temp_filename, 'rb') as f:
                    audio_bytes = f.read()
                
                # Clean up temporary file
                os.unlink(temp_filename)
                
                logger.info(f"Speech synthesized to file: {len(audio_bytes)} bytes")
                return audio_bytes
            else:
                # For direct playback, we would need a different approach
                # For now, just log the text
                logger.info(f"Speech synthesis requested: {text}")
                return None
                
        except Exception as e:
            logger.error(f"Error in speech synthesis: {e}")
            return None
    
    async def process_voice_command(self, audio_data: bytes) -> Dict[str, Any]:
        """Process voice command and return structured data"""
        try:
            # Recognize speech
            text = await self.recognize_from_bytes(audio_data)
            if not text:
                return {"error": "Could not recognize speech"}
            
            # Parse command using NLP
            command_data = self.nlp_processor.parse_command(text)
            
            return {
                "text": text,
                "command": command_data,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing voice command: {e}")
            return {"error": str(e)}
    
    def is_voice_recognition_available(self) -> bool:
        """Check if voice recognition is available"""
        return SPEECH_RECOGNITION_AVAILABLE and self.recognizer is not None
    
    def is_speech_synthesis_available(self) -> bool:
        """Check if speech synthesis is available"""
        return SPEECH_SYNTHESIS_AVAILABLE and self.synthesis_engine is not None
    
    def get_supported_languages(self) -> list:
        """Get list of supported languages"""
        return ["ru-RU", "en-US", "en-GB"]
    
    async def test_voice_recognition(self) -> Dict[str, Any]:
        """Test voice recognition functionality"""
        if not self.is_voice_recognition_available():
            return {"available": False, "error": "Voice recognition not available"}
        
        try:
            # Try to listen for a short duration
            text = await self.listen_microphone(timeout=2)
            
            return {
                "available": True,
                "test_result": text if text else "No speech detected",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "available": True,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def test_speech_synthesis(self) -> Dict[str, Any]:
        """Test speech synthesis functionality"""
        if not self.is_speech_synthesis_available():
            return {"available": False, "error": "Speech synthesis not available"}
        
        try:
            test_text = "Тест синтеза речи"
            audio_bytes = await self.synthesize_speech(test_text, save_to_file=True)
            
            return {
                "available": True,
                "test_result": "Synthesis successful" if audio_bytes else "Synthesis failed",
                "audio_size": len(audio_bytes) if audio_bytes else 0,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "available": True,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


# Global voice service instance
voice_service = VoiceService()
