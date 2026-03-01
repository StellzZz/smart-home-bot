"""Setup webhook for Telegram bot"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
RENDER_URL = os.getenv("RENDER_URL")  # https://your-app.onrender.com

def setup_webhook():
    """Setup webhook for Telegram bot"""
    if not TELEGRAM_TOKEN:
        print("❌ TELEGRAM_TOKEN not found!")
        return
    
    if not RENDER_URL:
        print("❌ RENDER_URL not found!")
        return
    
    webhook_url = f"{RENDER_URL}/webhook"
    
    # Set webhook
    response = requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook",
        json={
            "url": webhook_url,
            "secret_token": os.getenv("TELEGRAM_WEBHOOK_SECRET", "")
        }
    )
    
    if response.status_code == 200:
        print(f"✅ Webhook set to: {webhook_url}")
        print(f"📊 Response: {response.json()}")
    else:
        print(f"❌ Error setting webhook: {response.status_code}")
        print(f"📊 Response: {response.text}")

if __name__ == "__main__":
    setup_webhook()
