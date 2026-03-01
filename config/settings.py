"""Configuration settings for Smart Home Bot"""

import os
from typing import List, Optional
from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    """Application settings using Pydantic for validation"""
    
    # Telegram Bot Settings
    TELEGRAM_TOKEN: str
    TELEGRAM_WEBHOOK_URL: Optional[str] = None
    TELEGRAM_WEBHOOK_SECRET: Optional[str] = None
    
    # Security Settings
    TELEGRAM_USER_IDS: List[int] = []
    ALLOWED_USERNAMES: List[str] = []
    RATE_LIMIT_REQUESTS: int = 30
    RATE_LIMIT_PERIOD: int = 60  # seconds
    
    # Device Settings
    HOME_ASSISTANT_URL: str = "http://localhost:8123"
    HOME_ASSISTANT_TOKEN: Optional[str] = None
    
    # TV Settings (Android TV/Kiwi 2K)
    TV_IP_ADDRESS: str = "192.168.1.100"
    TV_PORT: int = 5555
    
    # Vacuum Settings (Xiaomi X20+)
    VACUUM_IP_ADDRESS: str = "192.168.1.101"
    VACUUM_TOKEN: Optional[str] = None
    
    # Light Settings (Xiaomi Smart Lights)
    LIGHT_GATEWAY_IP: str = "192.168.1.102"
    
    # Application Settings
    APP_NAME: str = "Smart Home Jarvis"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/smart_home.log"
    
    # Voice Recognition Settings
    SPEECH_RECOGNITION_ENABLED: bool = True
    SPEECH_SYNTHESIS_ENABLED: bool = True
    SPEECH_LANGUAGE: str = "ru-RU"
    
    # Database Settings (for future scaling)
    DATABASE_URL: str = "sqlite:///./smart_home.db"
    
    @validator('TELEGRAM_TOKEN')
    def validate_telegram_token(cls, v):
        if not v or len(v) < 20:
            raise ValueError('Invalid Telegram token')
        return v
    
    @validator('TELEGRAM_USER_IDS', pre=True)
    def parse_user_ids(cls, v):
        if isinstance(v, str):
            return [int(x.strip()) for x in v.split(',')]
        return v
    
    @validator('ALLOWED_USERNAMES', pre=True)
    def parse_usernames(cls, v):
        if isinstance(v, str):
            return [x.strip() for x in v.split(',')]
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()
