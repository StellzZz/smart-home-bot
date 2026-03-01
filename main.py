"""Main entry point for Smart Home Bot"""

import asyncio
import uvicorn
from contextlib import asynccontextmanager

from config.settings import settings
from config.logging_config import logger
from bot.bot_app import smart_home_bot


@asynccontextmanager
async def lifespan(app):
    """Manage application lifecycle"""
    # Startup
    logger.info("Starting Smart Home Bot...")
    await smart_home_bot.initialize()
    
    yield
    
    # Shutdown
    logger.info("Shutting down Smart Home Bot...")
    await smart_home_bot.cleanup()


async def run_polling():
    """Run bot with polling mode"""
    try:
        await smart_home_bot.run_polling()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")
        raise


async def run_webhook():
    """Run bot with webhook mode"""
    try:
        webhook_url = settings.TELEGRAM_WEBHOOK_URL
        if not webhook_url:
            logger.error("TELEGRAM_WEBHOOK_URL not configured")
            return
        
        await smart_home_bot.run_webhook(webhook_url)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")
        raise


def run_web_server():
    """Run web server with FastAPI"""
    try:
        # Configure FastAPI app
        app = smart_home_bot.web_app
        app.router.lifespan_context = lifespan
        
        # Run server
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=10000,
            log_level=settings.LOG_LEVEL.lower()
        )
        
    except Exception as e:
        logger.error(f"Web server error: {e}")
        raise


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        
        if mode == "polling":
            asyncio.run(run_polling())
        elif mode == "webhook":
            asyncio.run(run_webhook())
        elif mode == "web":
            run_web_server()
        else:
            print("Usage: python main.py [polling|webhook|web]")
            print("  polling - Run bot with polling")
            print("  webhook  - Run bot with webhook")
            print("  web      - Run web server only")
    else:
        # Default: run web server (for deployment platforms like Render)
        run_web_server()
