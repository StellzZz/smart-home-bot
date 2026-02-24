import os
import asyncio
import speech_recognition as sr
import sounddevice as sd
import numpy as np
import threading
import time
from jarvis_core import jarvis

class VoiceHandler:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.is_listening = False
        self.wake_word = "джарвис"
        self.sample_rate = 16000
        self.duration = 5  # секунд записи
        
    def listen_continuously(self):
        """Постоянное прослушивание команд"""
        print(f"{jarvis.name} активирован и слушает команды...")
        
        while self.is_listening:
            try:
                print("Слушаю...")
                # Записываем аудио через sounddevice
                audio_data = sd.rec(int(self.sample_rate * self.duration), 
                                 samplerate=self.sample_rate, 
                                 channels=1, 
                                 dtype=np.int16)
                sd.wait()  # ждём окончания записи
                
                # Конвертируем в формат для SpeechRecognition
                audio = sr.AudioData(audio_data.tobytes(), 
                                  sample_rate=self.sample_rate, 
                                  sample_width=2)
                
                try:
                    # Распознавание речи
                    text = self.recognize_speech(audio)
                    print(f"Распознано: {text}")
                    
                    # Проверка активационного слова
                    if self.wake_word in text.lower():
                        response = jarvis.process_command(text)
                        print(f"Джарвис: {response}")
                        
                except sr.UnknownValueError:
                    # Не удалось распознать речь
                    pass
                except Exception as e:
                    print(f"Ошибка распознавания: {e}")
                    
            except Exception as e:
                print(f"Ошибка микрофона: {e}")
                time.sleep(1)
    
    def recognize_speech(self, audio) -> str:
        """Распознавание речи"""
        try:
            # Временно используем Google Speech Recognition
            # Позже заменим на Vosk для оффлайн работы
            text = self.recognizer.recognize_google(audio, language="ru-RU")
            return text.lower()
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            print(f"Ошибка сервиса распознавания: {e}")
            return ""
    
    def start_listening(self):
        """Начать прослушивание"""
        self.is_listening = True
        self.listener_thread = threading.Thread(target=self.listen_continuously, daemon=True)
        self.listener_thread.start()
    
    def stop_listening(self):
        """Остановить прослушивание"""
        self.is_listening = False

# Глобальный обработчик голоса
voice_handler = VoiceHandler()
