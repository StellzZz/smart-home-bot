import os
import asyncio
import threading
try:
    from flask import Flask
except ImportError:
    print("Flask не найден, используем веб-сервер по умолчанию")
    Flask = None

from telegram_bot import create_app
# Временно отключаем голосовой модуль
try:
    from voice_handler import voice_handler
    VOICE_ENABLED = True
except ImportError:
    print("🎤 Голосовой модуль не найден, работает только Telegram")
    VOICE_ENABLED = False

try:
    from speech_synthesis import speech_synthesizer
    SPEECH_ENABLED = True
except ImportError:
    print("🔊 Синтез речи не найден")
    SPEECH_ENABLED = False

if Flask:
    app = Flask(__name__)

    @app.route("/")
    def home():
        return "🏠 Умный дом Джарвиса активен"
else:
    app = None

def run_voice_assistant():
    """Запуск голосового ассистента в отдельном потоке"""
    if VOICE_ENABLED:
        print("🎤 Запускаю голосового ассистента Джарвиса...")
        voice_handler.start_listening()
    else:
        print("🎤 Голосовой ассистент отключен")

def run_telegram_bot():
    """Запуск Telegram бота"""
    print("🤖 Запускаю Telegram бота Джарвиса...")
    import asyncio
    
    # Создаём event loop для потока
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        app_bot = create_app()
        loop.run_until_complete(app_bot.run_polling())
    except KeyboardInterrupt:
        print("🤖 Telegram бот остановлен")
    finally:
        loop.close()

if __name__ == "__main__":
    print("🏠 Запускаю умный дом Джарвиса...")
    
    # Запускаем голосового ассистента в отдельном потоке
    voice_thread = threading.Thread(target=run_voice_assistant, daemon=True)
    voice_thread.start()
    
    # Запускаем Telegram бота
    telegram_thread = threading.Thread(target=run_telegram_bot, daemon=True)
    telegram_thread.start()
    
    # Запускаем Flask сервер если доступен
    if app:
        app.run(host="0.0.0.0", port=10000)
    else:
        # Если Flask недоступен, просто держим программу работающей
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            print("👋 Джарвис отключается...")
