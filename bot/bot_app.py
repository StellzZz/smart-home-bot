"""Main Telegram bot application"""

import asyncio
from typing import Optional

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

from config.settings import settings
from config.logging_config import logger
from bot.handlers import bot_handlers
from services.auth_service import auth_service
from devices.device_manager import device_manager


class SmartHomeBot:
    """Main Smart Home Bot application"""
    
    def __init__(self):
        self.application = None
        self.web_app = FastAPI(title="Smart Home Bot API")
        self._setup_web_app()
    
    async def initialize(self):
        """Initialize bot and connect to devices"""
        try:
            # Initialize Telegram bot
            self.application = Application.builder().token(settings.TELEGRAM_TOKEN).build()
            self._setup_handlers()
            
            # Connect to all devices
            logger.info("Connecting to devices...")
            connection_results = await device_manager.connect_all()
            
            connected_count = sum(1 for result in connection_results.values() if result)
            total_count = len(connection_results)
            
            logger.info(f"Connected to {connected_count}/{total_count} devices")
            
            # Start cleanup task for expired sessions
            asyncio.create_task(self._cleanup_task())
            
            logger.info("Smart Home Bot initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing bot: {e}")
            raise
    
    def _setup_handlers(self):
        """Setup bot handlers"""
        if not self.application:
            raise ValueError("Application not initialized")
        
        # Command handlers
        self.application.add_handler(CommandHandler("start", bot_handlers.start_command))
        self.application.add_handler(CommandHandler("help", bot_handlers.help_command))
        self.application.add_handler(CommandHandler("status", bot_handlers.status_command))
        self.application.add_handler(CommandHandler("health", bot_handlers.health_command))
        
        # Light commands
        self.application.add_handler(CommandHandler("light_on", lambda u, c: bot_handlers.light_command(u, c, "on")))
        self.application.add_handler(CommandHandler("light_off", lambda u, c: bot_handlers.light_command(u, c, "off")))
        
        # TV commands
        self.application.add_handler(CommandHandler("tv_on", lambda u, c: bot_handlers.tv_command(u, c)))
        self.application.add_handler(CommandHandler("tv_off", lambda u, c: bot_handlers.tv_command(u, c)))
        self.application.add_handler(CommandHandler("tv", bot_handlers.tv_command))
        
        # Vacuum commands
        self.application.add_handler(CommandHandler("vacuum_start", lambda u, c: bot_handlers.vacuum_command(u, c, "start")))
        self.application.add_handler(CommandHandler("vacuum_pause", lambda u, c: bot_handlers.vacuum_command(u, c, "pause")))
        self.application.add_handler(CommandHandler("vacuum_dock", lambda u, c: bot_handlers.vacuum_command(u, c, "dock")))
        self.application.add_handler(CommandHandler("vacuum_find", lambda u, c: bot_handlers.vacuum_command(u, c, "find")))
        
        # Message handlers
        self.application.add_handler(MessageHandler(filters.VOICE, bot_handlers.voice_message_handler))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot_handlers.text_message_handler))
        
        # Callback query handler
        self.application.add_handler(CallbackQueryHandler(bot_handlers.callback_query_handler))
    
    def _setup_web_app(self):
        """Setup FastAPI web application"""
        
        @self.web_app.get("/")
        async def root():
            return {"message": "Smart Home Bot API", "status": "running"}
        
        @self.web_app.get("/health")
        async def health_check():
            try:
                health_data = await device_manager.health_check()
                return health_data
            except Exception as e:
                logger.error(f"Health check error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.web_app.get("/status")
        async def get_status():
            try:
                status_data = await device_manager.get_all_status()
                return status_data
            except Exception as e:
                logger.error(f"Status check error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.web_app.post("/webhook")
        async def telegram_webhook(request: Request):
            """Handle Telegram webhook"""
            try:
                # Validate webhook secret if configured
                secret_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
                if not auth_service.validate_webhook_secret(secret_token or ""):
                    logger.warning("Invalid webhook secret")
                    raise HTTPException(status_code=403, detail="Invalid secret")
                
                # Get update data
                update_data = await request.json()
                
                # Create Update object
                update = Update.de_json(update_data, self.application.bot)
                
                # Process update
                await self.application.process_update(update)
                
                return JSONResponse(content={"ok": True})
                
            except Exception as e:
                logger.error(f"Webhook error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.web_app.get("/security/stats")
        async def security_stats():
            """Get security statistics"""
            try:
                stats = auth_service.get_security_stats()
                return stats
            except Exception as e:
                logger.error(f"Security stats error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.web_app.post("/device/{device_type}/{command}")
        async def device_command(device_type: str, command: str, request: Request):
            """Execute device command via API"""
            try:
                # Get command parameters
                params = await request.json() if request.headers.get("content-type") == "application/json" else {}
                
                # Execute command
                success = await device_manager.execute_device_command(device_type, command, params)
                
                return {
                    "success": success,
                    "device_type": device_type,
                    "command": command,
                    "params": params
                }
                
            except Exception as e:
                logger.error(f"Device command error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    async def run_polling(self):
        """Run bot with polling"""
        try:
            await self.initialize()
            logger.info("Starting bot polling...")
            await self.application.run_polling(drop_pending_updates=True)
        except Exception as e:
            logger.error(f"Error running polling: {e}")
            raise
        finally:
            await self.cleanup()
    
    async def run_webhook(self, webhook_url: str):
        """Run bot with webhook"""
        try:
            await self.initialize()
            
            # Set webhook
            await self.application.bot.set_webhook(
                url=webhook_url,
                secret_token=settings.TELEGRAM_WEBHOOK_SECRET
            )
            
            logger.info(f"Webhook set to: {webhook_url}")
            
            # Keep the application running
            await self.application.initialize()
            await self.application.start()
            
            # Run forever
            while True:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Error running webhook: {e}")
            raise
        finally:
            await self.cleanup()
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            logger.info("Cleaning up...")
            
            # Disconnect from devices
            if device_manager:
                await device_manager.disconnect_all()
            
            # Stop bot application
            if self.application:
                await self.application.stop()
                await self.application.shutdown()
            
            logger.info("Cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    async def _cleanup_task(self):
        """Background cleanup task"""
        while True:
            try:
                # Clean up expired sessions
                auth_service.cleanup_expired_sessions()
                
                # Sleep for 1 hour
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")
                await asyncio.sleep(300)  # Sleep 5 minutes on error


# Global bot instance
smart_home_bot = SmartHomeBot()
