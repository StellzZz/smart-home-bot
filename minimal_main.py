import os
import asyncio
import threading
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Загружаем переменные окружения
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

if not TOKEN:
    print("❌ TELEGRAM_TOKEN не найден в .env файле!")
    exit(1)

class JarvisBot:
    def __init__(self):
        self.devices = {
            "lights": {"hallway": False, "kitchen": False, "room": False, "bathroom": False, "toilet": False},
            "tv": {"on": False, "volume": 50},
            "vacuum": {"cleaning": False, "docked": True}
        }
    
    def toggle_light(self, room: str, state: bool) -> str:
        if room in self.devices["lights"]:
            self.devices["lights"][room] = state
            action = "включён" if state else "выключен"
            return f"Свет в {self.get_room_name(room)} {action}"
        return f"Неизвестная комната: {room}"
    
    def toggle_tv(self, state: bool) -> str:
        self.devices["tv"]["on"] = state
        action = "включен" if state else "выключен"
        return f"Телевизор {action}"
    
    def start_vacuum(self) -> str:
        self.devices["vacuum"]["cleaning"] = True
        self.devices["vacuum"]["docked"] = False
        return "Начинаю уборку, сэр"
    
    def dock_vacuum(self) -> str:
        self.devices["vacuum"]["cleaning"] = False
        self.devices["vacuum"]["docked"] = True
        return "Возвращаюсь на базу"
    
    def get_vacuum_status(self) -> str:
        if self.devices["vacuum"]["cleaning"]:
            return "Пылесос выполняет уборку"
        elif self.devices["vacuum"]["docked"]:
            return "Пылесос на базе, заряжен"
        else:
            return "Пылесос в режиме ожидания"
    
    def get_room_name(self, room: str) -> str:
        room_names = {
            "hallway": "прихожей",
            "kitchen": "кухне", 
            "room": "комнате",
            "bathroom": "ванной",
            "toilet": "туалете"
        }
        return room_names.get(room, room)
    
    def get_all_status(self) -> str:
        lights_on = sum(1 for light in self.devices["lights"].values() if light)
        tv_status = "включен" if self.devices["tv"]["on"] else "выключен"
        vac_status = self.get_vacuum_status()
        
        return f"Свет: {lights_on} из {len(self.devices['lights'])} комнат включено\nТелевизор: {tv_status}\nПылесос: {vac_status}"

# Создаём экземпляр Джарвиса
jarvis = JarvisBot()

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏠 *Умный дом Джарвиса*\n\n"
        "📱 *Команды:*\n"
        "/light_on [room] - Включить свет\n"
        "/light_off [room] - Выключить свет\n"
        "/tv_on - Включить телевизор\n"
        "/tv_off - Выключить телевизор\n"
        "/vacuum_start - Начать уборку\n"
        "/vacuum_dock - Вернуть на базу\n"
        "/status - Статус устройств\n\n"
        "🏠 *Комнаты:*\n"
        "hallway - прихожая\n"
        "kitchen - кухня\n"
        "room - комната\n"
        "bathroom - ванная\n"
        "toilet - туалет\n\n"
        "🤖 *Джарвис готов к работе!*"
    )

async def light_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        room = context.args[0] if context.args else "all"
        if room == "all":
            response = "Весь свет включён"
        else:
            response = jarvis.toggle_light(room, True)
        await update.message.reply_text(f"💡 {response}")
    except IndexError:
        await update.message.reply_text("❌ Использование: /light_on [room]")

async def light_off_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        room = context.args[0] if context.args else "all"
        if room == "all":
            response = "Весь свет выключен"
        else:
            response = jarvis.toggle_light(room, False)
        await update.message.reply_text(f"💡 {response}")
    except IndexError:
        await update.message.reply_text("❌ Использование: /light_off [room]")

async def tv_on_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = jarvis.toggle_tv(True)
    await update.message.reply_text(f"📺 {response}")

async def tv_off_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = jarvis.toggle_tv(False)
    await update.message.reply_text(f"📺 {response}")

async def vacuum_start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = jarvis.start_vacuum()
    await update.message.reply_text(f"🤖 {response}")

async def vacuum_dock_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = jarvis.dock_vacuum()
    await update.message.reply_text(f"🤖 {response}")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = jarvis.get_all_status()
    await update.message.reply_text(f"🏠 *Статус устройств:*\n\n{response}")

def create_app():
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Регистрируем команды
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("light_on", light_command))
    app.add_handler(CommandHandler("light_off", light_off_command))
    app.add_handler(CommandHandler("tv_on", tv_on_command))
    app.add_handler(CommandHandler("tv_off", tv_off_command))
    app.add_handler(CommandHandler("vacuum_start", vacuum_start_command))
    app.add_handler(CommandHandler("vacuum_dock", vacuum_dock_command))
    app.add_handler(CommandHandler("status", status_command))
    
    return app

def run_telegram_bot():
    print("🤖 Запускаю Telegram бота Джарвиса...")
    import asyncio
    
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
    
    # Запускаем Telegram бота
    telegram_thread = threading.Thread(target=run_telegram_bot, daemon=True)
    telegram_thread.start()
    
    # Держим программу работающей
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print("👋 Джарвис отключается...")
