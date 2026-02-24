import os
import asyncio
from jarvis_core import jarvis

class SpeechSynthesis:
    def __init__(self):
        self.voice_type = "british"  # британский акцент
        
    def speak(self, text: str):
        """Синтез и воспроизведение речи"""
        try:
            # Временно используем gTTS (Google Text-to-Speech)
            # Позже заменим на Piper TTS для оффлайн работы
            from gtts import gTTS
            import pygame
            
            # Создаём аудиофайл
            tts = gTTS(text=text, lang='en', slow=False)  # английский для британского акцента
            filename = "temp_speech.mp3"
            tts.save(filename)
            
            # Воспроизводим аудио
            pygame.mixer.init()
            pygame.mixer.music.load(filename)
            pygame.mixer.music.play()
            
            # Удаляем временный файл
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            pygame.mixer.music.stop()
            pygame.mixer.quit()
            
            os.remove(filename)
            
        except Exception as e:
            print(f"Ошибка синтеза речи: {e}")
            # Запасной вариант
            print(f"{jarvis.name}: {text}")
    
    def speak_response(self, response: str):
        """Произнести ответ Джарвиса"""
        print(f"{jarvis.name}: {response}")
        self.speak(response)

# Глобальный синтезатор речи
speech_synthesizer = SpeechSynthesis()
