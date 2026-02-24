import os
import asyncio
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("TELEGRAM_TOKEN")

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is alive"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот работает!")

def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    loop.run_until_complete(application.run_polling())

if __name__ == "__main__":
    from threading import Thread
    Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=10000)

