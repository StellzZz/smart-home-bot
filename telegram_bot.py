import os
import asyncio
from dotenv import load_dotenv
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from jarvis_core import jarvis
from device_controller import device_controller
from speech_synthesis import speech_synthesizer

# Загружаем переменные окружения
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    print("❌ TELEGRAM_TOKEN не найден в .env файле!")
    exit(1)

class TelegramBotHandler:
    def __init__(self):
        self.bot = None
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start"""
        await update.message.reply_text(
            "🏠 *Умный дом Джарвиса*\n\n"
            "📱 *Основные команды:*\n"
            "/light_on [room] - Включить свет\n"
            "/light_off [room] - Выключить свет\n"
            "/tv_on - Включить телевизор\n"
            "/tv_off - Выключить телевизор\n"
            "/tv [action] - Управление TV (on/off/netflix/youtube)\n"
            "/vacuum_start - Начать уборку\n"
            "/vacuum_dock - Вернуть на базу\n"
            "/vacuum [action] - Управление пылесосом (start/dock/status)\n"
            "/status - Статус всех устройств\n\n"
            "🏠 *Комнаты:*\n"
            "hallway - прихожая\n"
            "kitchen - кухня\n"
            "room - комната\n"
            "bathroom - ванная\n"
            "toilet - туалет\n\n"
            f"🤖 *Джарвис готов к работе!*"
        )
    
    async def light_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Управление светом"""
        try:
            room = context.args[0] if context.args else "all"
            if room == "all":
                response = jarvis.toggle_all_lights(True)
            else:
                room_map = {
                    "hallway": "hallway",
                    "прихожая": "hallway", 
                    "kitchen": "kitchen",
                    "кухня": "kitchen",
                    "room": "room",
                    "комната": "room",
                    "bathroom": "bathroom",
                    "ванная": "bathroom",
                    "toilet": "toilet",
                    "туалет": "toilet"
                }
                room_key = room_map.get(room, room)
                if room_key in jarvis.devices["lights"]:
                    response = jarvis.toggle_light(room_key, True)
                else:
                    response = f"Неизвестная комната: {room}"
            
            await update.message.reply_text(f"💡 {response}")
            
            # Выполняем команду на устройстве
            await device_controller.execute_device_command("light", room_key or room, "on")
            
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка: {e}")
    
    async def light_off_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Выключить свет"""
        try:
            room = context.args[0] if context.args else "all"
            if room == "all":
                response = jarvis.toggle_all_lights(False)
            else:
                room_map = {
                    "hallway": "hallway",
                    "прихожая": "hallway",
                    "kitchen": "kitchen", 
                    "кухня": "kitchen",
                    "room": "room",
                    "комната": "room",
                    "bathroom": "bathroom",
                    "ванная": "bathroom",
                    "toilet": "toilet",
                    "туалет": "toilet"
                }
                room_key = room_map.get(room, room)
                if room_key in jarvis.devices["lights"]:
                    response = jarvis.toggle_light(room_key, False)
                else:
                    response = f"Неизвестная комната: {room}"
            
            await update.message.reply_text(f"💡 {response}")
            
            # Выполняем команду на устройстве
            await device_controller.execute_device_command("light", room_key or room, "off")
            
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка: {e}")
    
    async def tv_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Управление телевизором"""
        try:
            action = context.args[0] if context.args else "status"
            
            if action == "on" or action == "включить":
                response = jarvis.toggle_tv(True)
                await device_controller.execute_device_command("tv", "on")
            elif action == "off" or action == "выключить":
                response = jarvis.toggle_tv(False)
                await device_controller.execute_device_command("tv", "off")
            elif action == "netflix":
                response = jarvis.tv_control("netflix")
                await device_controller.execute_device_command("tv", "netflix")
            elif action == "youtube":
                response = jarvis.tv_control("youtube")
                await device_controller.execute_device_command("tv", "youtube")
            else:
                response = f"Неизвестная команда: {action}"
            
            await update.message.reply_text(f"📺 {response}")
            
        except IndexError:
            await update.message.reply_text("❌ Использование: /tv [on|off|netflix|youtube]")
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка: {e}")
    
    async def vacuum_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Управление пылесосом"""
        try:
            action = context.args[0] if context.args else "status"
            
            if action == "start" or action == "начать":
                response = jarvis.start_vacuum()
                await device_controller.execute_device_command("vacuum", "start")
            elif action == "dock" or action == "база":
                response = jarvis.dock_vacuum()
                await device_controller.execute_device_command("vacuum", "dock")
            elif action == "status":
                response = jarvis.get_vacuum_status()
            else:
                response = f"Неизвестная команда: {action}"
            
            await update.message.reply_text(f"🤖 {response}")
            
        except IndexError:
            await update.message.reply_text("❌ Использование: /vacuum [start|dock|status]")
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка: {e}")
    
    async def tv_on_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Включить телевизор"""
        response = jarvis.toggle_tv(True)
        await update.message.reply_text(f"📺 {response}")
    
    async def tv_off_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Выключить телевизор"""
        response = jarvis.toggle_tv(False)
        await update.message.reply_text(f"📺 {response}")
    
    async def vacuum_start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начать уборку"""
        response = jarvis.start_vacuum()
        await update.message.reply_text(f"🤖 {response}")
    
    async def vacuum_dock_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Вернуть на базу"""
        response = jarvis.dock_vacuum()
        await update.message.reply_text(f"🤖 {response}")
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Статус всех устройств"""
        try:
            response = jarvis.get_all_status()
            await update.message.reply_text(f"🏠 *Статус устройств:*\n\n{response}")
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка: {e}")

# Создаём обработчик
telegram_handler = TelegramBotHandler()

def create_app():
    """Создание Telegram приложения"""
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Регистрируем команды
    app.add_handler(CommandHandler("start", telegram_handler.start_command))
    app.add_handler(CommandHandler("light_on", telegram_handler.light_command))
    app.add_handler(CommandHandler("light_off", telegram_handler.light_off_command))
    app.add_handler(CommandHandler("tv", telegram_handler.tv_command))
    app.add_handler(CommandHandler("tv_on", telegram_handler.tv_on_command))
    app.add_handler(CommandHandler("tv_off", telegram_handler.tv_off_command))
    app.add_handler(CommandHandler("vacuum", telegram_handler.vacuum_command))
    app.add_handler(CommandHandler("vacuum_start", telegram_handler.vacuum_start_command))
    app.add_handler(CommandHandler("vacuum_dock", telegram_handler.vacuum_dock_command))
    app.add_handler(CommandHandler("status", telegram_handler.status_command))
    
    return app
