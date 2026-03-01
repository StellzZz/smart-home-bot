"""Telegram bot handlers for Smart Home Bot"""

import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler

from config.settings import settings
from config.logging_config import logger
from services.auth_service import auth_service
from services.voice_service import voice_service
from devices.device_manager import device_manager
from utils.decorators import authorized_users_only, rate_limit, handle_errors
from utils.validators import CommandValidator, NaturalLanguageProcessor


class BotHandlers:
    """Class containing all bot handlers"""
    
    def __init__(self):
        self.nlp_processor = NaturalLanguageProcessor()
    
    @authorized_users_only
    @rate_limit
    @handle_errors
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        
        welcome_text = (
            f"🏠 *Добро пожаловать в Умный Дом Джарвиса!*\n\n"
            f"👋 Привет, {user.full_name}!\n\n"
            f"📱 *Основные команды:*\n"
            f"/light_on [комната] - Включить свет\n"
            f"/light_off [комната] - Выключить свет\n"
            f"/tv_on - Включить телевизор\n"
            f"/tv_off - Выключить телевизор\n"
            f"/tv [приложение] - Запустить приложение (netflix/youtube)\n"
            f"/vacuum_start - Начать уборку\n"
            f"/vacuum_dock - Вернуть на базу\n"
            f"/status - Статус всех устройств\n"
            f"/help - Показать справку\n\n"
            f"🏠 *Комнаты:*\n"
            f"hallway - прихожая\n"
            f"kitchen - кухня\n"
            f"room - комната\n"
            f"bathroom - ванная\n"
            f"toilet - туалет\n"
            f"all - все комнаты\n\n"
            f"🎤 Также поддерживаются голосовые команды!"
        )
        
        # Create inline keyboard
        keyboard = [
            [
                InlineKeyboardButton("💡 Свет", callback_data="menu_lights"),
                InlineKeyboardButton("📺 ТВ", callback_data="menu_tv"),
            ],
            [
                InlineKeyboardButton("🤖 Пылесос", callback_data="menu_vacuum"),
                InlineKeyboardButton("📊 Статус", callback_data="status"),
            ],
            [
                InlineKeyboardButton("❓ Помощь", callback_data="help"),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_text,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
    
    @authorized_users_only
    @rate_limit
    @handle_errors
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = (
            "📖 *Справка по командам:*\n\n"
            "💡 *Управление светом:*\n"
            "• `/light_on [комната]` - Включить свет\n"
            "• `/light_off [комната]` - Выключить свет\n"
            "• `/light_brightness [комната] [0-100]` - Установить яркость\n\n"
            "📺 *Управление телевизором:*\n"
            "• `/tv_on` - Включить телевизор\n"
            "• `/tv_off` - Выключить телевизор\n"
            "• `/tv netflix` - Открыть Netflix\n"
            "• `/tv youtube` - Открыть YouTube\n"
            "• `/tv_volume up/down` - Громкость\n\n"
            "🤖 *Управление пылесосом:*\n"
            "• `/vacuum_start` - Начать уборку\n"
            "• `/vacuum_pause` - Пауза\n"
            "• `/vacuum_dock` - На базу\n"
            "• `/vacuum_find` - Найти пылесос\n\n"
            "📊 *Информация:*\n"
            "• `/status` - Статус всех устройств\n"
            "• `/health` - Проверка системы\n\n"
            "🎤 *Голосовые команды:*\n"
            "Отправьте голосовое сообщение с командой:\n"
            "• \"Включи свет в комнате\"\n"
            "• \"Выключи телевизор\"\n"
            "• \"Начни уборку\"\n"
            "• \"Покажи статус\""
        )
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    @authorized_users_only
    @rate_limit
    @handle_errors
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        try:
            # Get all device status
            status_data = await device_manager.get_all_status()
            
            # Format status message
            status_text = "📊 *Статус устройств:*\n\n"
            
            # Lights status
            if "lights" in status_data:
                lights_status = status_data["lights"]
                lights_on = sum(1 for light in lights_status.values() if isinstance(light, dict) and light.get("status"))
                total_lights = len(lights_status)
                status_text += f"💡 Свет: {lights_on}/{total_lights} включено\n"
            
            # TV status
            if "tv" in status_data:
                tv_status = status_data["tv"]
                tv_on = tv_status.get("on", False)
                current_app = tv_status.get("current_app")
                tv_text = "включен" if tv_on else "выключен"
                app_text = f" ({current_app})" if current_app else ""
                status_text += f"📺 Телевизор: {tv_text}{app_text}\n"
            
            # Vacuum status
            if "vacuum" in status_data:
                vacuum_status = status_data["vacuum"]
                state = vacuum_status.get("state", "unknown")
                battery = vacuum_status.get("battery", 0)
                
                state_map = {
                    "charging": "на базе",
                    "cleaning": "убирается",
                    "returning": "возвращается",
                    "paused": "на паузе",
                    "idle": "в режиме ожидания"
                }
                
                state_text = state_map.get(state, state)
                status_text += f"🤖 Пылесос: {state_text}, заряд {battery}%\n"
            
            status_text += f"\n🕐 Обновлено: {datetime.now().strftime('%H:%M:%S')}"
            
            await update.message.reply_text(status_text, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in status command: {e}")
            await update.message.reply_text("❌ Не удалось получить статус устройств")
    
    @authorized_users_only
    @rate_limit
    @handle_errors
    async def health_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /health command"""
        try:
            health_data = await device_manager.health_check()
            
            health_text = "🏥 *Проверка системы:*\n\n"
            
            for device_name, device_health in health_data["devices"].items():
                status_emoji = "✅" if device_health["online"] else "❌"
                device_names = {
                    "lights": "Свет",
                    "tv": "Телевизор", 
                    "vacuum": "Пылесос"
                }
                device_name_ru = device_names.get(device_name, device_name)
                
                health_text += f"{status_emoji} {device_name_ru}: {device_health['status']}\n"
                
                if device_health.get("last_error"):
                    health_text += f"   Ошибка: {device_health['last_error']}\n"
            
            overall_status = health_data["overall_status"]
            status_emoji = "✅" if overall_status == "healthy" else "⚠️"
            
            status_map = {
                "healthy": "Исправна",
                "degraded": "Деградирована",
                "critical": "Критическая"
            }
            
            health_text += f"\n{status_emoji} Общая система: {status_map.get(overall_status, overall_status)}"
            
            await update.message.reply_text(health_text, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in health command: {e}")
            await update.message.reply_text("❌ Не удалось выполнить проверку системы")
    
    @authorized_users_only
    @rate_limit
    @handle_errors
    async def light_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE, action: str):
        """Handle light commands"""
        try:
            # Get room from command arguments
            room = "all"
            if context.args:
                room = CommandValidator.validate_room(context.args[0])
                if not room:
                    await update.message.reply_text("❌ Неизвестная комната")
                    return
            
            # Execute command
            if action == "on":
                success = await device_manager.toggle_light(room, True)
                response_text = f"💡 Свет в {self._get_room_name(room)} включен" if success else "❌ Не удалось включить свет"
            elif action == "off":
                success = await device_manager.toggle_light(room, False)
                response_text = f"💡 Свет в {self._get_room_name(room)} выключен" if success else "❌ Не удалось выключить свет"
            else:
                response_text = "❌ Неизвестное действие"
            
            await update.message.reply_text(response_text)
            
        except Exception as e:
            logger.error(f"Error in light command: {e}")
            await update.message.reply_text("❌ Ошибка выполнения команды")
    
    @authorized_users_only
    @rate_limit
    @handle_errors
    async def tv_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle TV commands"""
        try:
            if not context.args:
                await update.message.reply_text("❌ Укажите команду: on, off, netflix, youtube")
                return
            
            action = context.args[0].lower()
            
            if action in ["on", "включить"]:
                success = await device_manager.toggle_tv(True)
                response_text = "📺 Телевизор включен" if success else "❌ Не удалось включить телевизор"
            elif action in ["off", "выключить"]:
                success = await device_manager.toggle_tv(False)
                response_text = "📺 Телевизор выключен" if success else "❌ Не удалось выключить телевизор"
            elif action in ["netflix"]:
                success = await device_manager.launch_tv_app("netflix")
                response_text = "📺 Netflix запущен" if success else "❌ Не удалось запустить Netflix"
            elif action in ["youtube"]:
                success = await device_manager.launch_tv_app("youtube")
                response_text = "📺 YouTube запущен" if success else "❌ Не удалось запустить YouTube"
            else:
                response_text = "❌ Неизвестная команда"
            
            await update.message.reply_text(response_text)
            
        except Exception as e:
            logger.error(f"Error in TV command: {e}")
            await update.message.reply_text("❌ Ошибка выполнения команды")
    
    @authorized_users_only
    @rate_limit
    @handle_errors
    async def vacuum_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE, action: str):
        """Handle vacuum commands"""
        try:
            if action == "start":
                success = await device_manager.start_vacuum()
                response_text = "🤖 Уборка начата" if success else "❌ Не удалось начать уборку"
            elif action == "dock":
                success = await device_manager.dock_vacuum()
                response_text = "🤖 Пылесос возвращается на базу" if success else "❌ Не удалось отправить на базу"
            elif action == "pause":
                success = await device_manager.pause_vacuum()
                response_text = "🤖 Уборка приостановлена" if success else "❌ Не удалось приостановить уборку"
            elif action == "find":
                success = await device_manager.find_vacuum()
                response_text = "🔊 Пылесос подает звуковой сигнал" if success else "❌ Не удалось найти пылесос"
            else:
                response_text = "❌ Неизвестная команда"
            
            await update.message.reply_text(response_text)
            
        except Exception as e:
            logger.error(f"Error in vacuum command: {e}")
            await update.message.reply_text("❌ Ошибка выполнения команды")
    
    @authorized_users_only
    @rate_limit
    @handle_errors
    async def voice_message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle voice messages"""
        try:
            if not voice_service.is_voice_recognition_available():
                await update.message.reply_text("❌ Распознавание голоса недоступно")
                return
            
            voice = update.message.voice
            if not voice:
                return
            
            # Download voice file
            voice_file = await voice.get_file()
            voice_bytes = await voice_file.download_as_bytearray()
            
            # Process voice command
            result = await voice_service.process_voice_command(voice_bytes)
            
            if "error" in result:
                await update.message.reply_text(f"❌ {result['error']}")
                return
            
            recognized_text = result["text"]
            command_data = result["command"]
            
            # Send recognition result
            await update.message.reply_text(f"🎤 Распознано: \"{recognized_text}\"")
            
            # Execute command if parsed successfully
            if command_data and command_data.get("device_type"):
                await self._execute_parsed_command(update, command_data)
            else:
                await update.message.reply_text("❌ Не удалось распознать команду")
            
        except Exception as e:
            logger.error(f"Error processing voice message: {e}")
            await update.message.reply_text("❌ Ошибка обработки голосового сообщения")
    
    @authorized_users_only
    @rate_limit
    @handle_errors
    async def text_message_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages (natural language processing)"""
        try:
            text = update.message.text
            
            # Parse command using NLP
            command_data = self.nlp_processor.parse_command(text)
            
            if command_data and command_data.get("device_type"):
                await self._execute_parsed_command(update, command_data)
            else:
                # If not a command, provide help
                await update.message.reply_text(
                    "❓ Не распознана команда. Используйте /help для справки."
                )
            
        except Exception as e:
            logger.error(f"Error processing text message: {e}")
            await update.message.reply_text("❌ Ошибка обработки сообщения")
    
    async def _execute_parsed_command(self, update: Update, command_data: Dict[str, Any]):
        """Execute parsed command"""
        try:
            device_type = command_data.get("device_type")
            action = command_data.get("action")
            room = command_data.get("room")
            
            if device_type == "light":
                if action == "on":
                    success = await device_manager.toggle_light(room or "all", True)
                    response = f"💡 Свет в {self._get_room_name(room or 'all')} включен" if success else "❌ Не удалось включить свет"
                elif action == "off":
                    success = await device_manager.toggle_light(room or "all", False)
                    response = f"💡 Свет в {self._get_room_name(room or 'all')} выключен" if success else "❌ Не удалось выключить свет"
                else:
                    response = "❌ Неизвестное действие для света"
            
            elif device_type == "tv":
                if action == "on":
                    success = await device_manager.toggle_tv(True)
                    response = "📺 Телевизор включен" if success else "❌ Не удалось включить телевизор"
                elif action == "off":
                    success = await device_manager.toggle_tv(False)
                    response = "📺 Телевизор выключен" if success else "❌ Не удалось выключить телевизор"
                elif action in ["netflix", "youtube"]:
                    success = await device_manager.launch_tv_app(action)
                    response = f"📺 {action.capitalize()} запущен" if success else f"❌ Не удалось запустить {action}"
                else:
                    response = "❌ Неизвестное действие для ТВ"
            
            elif device_type == "vacuum":
                if action == "start":
                    success = await device_manager.start_vacuum()
                    response = "🤖 Уборка начата" if success else "❌ Не удалось начать уборку"
                elif action == "dock":
                    success = await device_manager.dock_vacuum()
                    response = "🤖 Пылесос возвращается на базу" if success else "❌ Не удалось отправить на базу"
                else:
                    response = "❌ Неизвестное действие для пылесоса"
            
            elif device_type == "status":
                await self.status_command(update, None)
                return
            
            else:
                response = "❌ Неизвестное устройство"
            
            await update.message.reply_text(response)
            
        except Exception as e:
            logger.error(f"Error executing parsed command: {e}")
            await update.message.reply_text("❌ Ошибка выполнения команды")
    
    async def callback_query_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline keyboard callbacks"""
        query = update.callback_query
        await query.answer()
        
        try:
            data = query.data
            
            if data == "menu_lights":
                keyboard = [
                    [InlineKeyboardButton("💡 Включить все", callback_data="light_all_on")],
                    [InlineKeyboardButton("🌙 Выключить все", callback_data="light_all_off")],
                    [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text("💡 Управление светом:", reply_markup=reply_markup)
            
            elif data == "menu_tv":
                keyboard = [
                    [InlineKeyboardButton("📺 Включить", callback_data="tv_on")],
                    [InlineKeyboardButton("📺 Выключить", callback_data="tv_off")],
                    [InlineKeyboardButton("🎬 Netflix", callback_data="tv_netflix")],
                    [InlineKeyboardButton("🎥 YouTube", callback_data="tv_youtube")],
                    [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text("📺 Управление телевизором:", reply_markup=reply_markup)
            
            elif data == "menu_vacuum":
                keyboard = [
                    [InlineKeyboardButton("🤖 Начать уборку", callback_data="vacuum_start")],
                    [InlineKeyboardButton("⏸️ Пауза", callback_data="vacuum_pause")],
                    [InlineKeyboardButton("🏠 На базу", callback_data="vacuum_dock")],
                    [InlineKeyboardButton("🔊 Найти", callback_data="vacuum_find")],
                    [InlineKeyboardButton("🔙 Назад", callback_data="main_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text("🤖 Управление пылесосом:", reply_markup=reply_markup)
            
            elif data == "status":
                await self.status_command(update, context)
            
            elif data == "help":
                await self.help_command(update, context)
            
            elif data == "main_menu":
                await self.start_command(update, context)
            
            # Handle specific actions
            elif data.startswith("light_"):
                if data == "light_all_on":
                    success = await device_manager.toggle_all_lights(True)
                    response = "💡 Весь свет включен" if success else "❌ Не удалось включить свет"
                elif data == "light_all_off":
                    success = await device_manager.toggle_all_lights(False)
                    response = "💡 Весь свет выключен" if success else "❌ Не удалось выключить свет"
                await query.edit_message_text(response)
            
            elif data.startswith("tv_"):
                if data == "tv_on":
                    success = await device_manager.toggle_tv(True)
                    response = "📺 Телевизор включен" if success else "❌ Не удалось включить телевизор"
                elif data == "tv_off":
                    success = await device_manager.toggle_tv(False)
                    response = "📺 Телевизор выключен" if success else "❌ Не удалось выключить телевизор"
                elif data == "tv_netflix":
                    success = await device_manager.launch_tv_app("netflix")
                    response = "📺 Netflix запущен" if success else "❌ Не удалось запустить Netflix"
                elif data == "tv_youtube":
                    success = await device_manager.launch_tv_app("youtube")
                    response = "📺 YouTube запущен" if success else "❌ Не удалось запустить YouTube"
                await query.edit_message_text(response)
            
            elif data.startswith("vacuum_"):
                if data == "vacuum_start":
                    success = await device_manager.start_vacuum()
                    response = "🤖 Уборка начата" if success else "❌ Не удалось начать уборку"
                elif data == "vacuum_pause":
                    success = await device_manager.pause_vacuum()
                    response = "🤖 Уборка приостановлена" if success else "❌ Не удалось приостановить уборку"
                elif data == "vacuum_dock":
                    success = await device_manager.dock_vacuum()
                    response = "🤖 Пылесос возвращается на базу" if success else "❌ Не удалось отправить на базу"
                elif data == "vacuum_find":
                    success = await device_manager.find_vacuum()
                    response = "🔊 Пылесос подает звуковой сигнал" if success else "❌ Не удалось найти пылесос"
                await query.edit_message_text(response)
            
        except Exception as e:
            logger.error(f"Error in callback query handler: {e}")
            await query.edit_message_text("❌ Ошибка обработки запроса")
    
    def _get_room_name(self, room: str) -> str:
        """Get Russian room name"""
        room_names = {
            "hallway": "прихожей",
            "kitchen": "кухне",
            "room": "комнате",
            "bathroom": "ванной",
            "toilet": "туалете",
            "all": "всех комнатах"
        }
        return room_names.get(room, room)


# Global handlers instance
bot_handlers = BotHandlers()
