"""Validation utilities for Smart Home Bot"""

import re
from typing import Optional, List, Dict, Any
from enum import Enum

from config.logging_config import logger


class RoomType(Enum):
    """Supported room types"""
    HALLWAY = "hallway"
    KITCHEN = "kitchen"
    ROOM = "room"
    BATHROOM = "bathroom"
    TOILET = "toilet"
    ALL = "all"


class DeviceType(Enum):
    """Supported device types"""
    LIGHT = "light"
    TV = "tv"
    VACUUM = "vacuum"


class TVAction(Enum):
    """Supported TV actions"""
    ON = "on"
    OFF = "off"
    NETFLIX = "netflix"
    YOUTUBE = "youtube"
    VOLUME_UP = "volume_up"
    VOLUME_DOWN = "volume_down"


class VacuumAction(Enum):
    """Supported vacuum actions"""
    START = "start"
    DOCK = "dock"
    STATUS = "status"
    PAUSE = "pause"


class CommandValidator:
    """Validator for bot commands"""
    
    # Room mapping for natural language processing
    ROOM_MAPPING = {
        "прихожая": RoomType.HALLWAY.value,
        "коридор": RoomType.HALLWAY.value,
        "hallway": RoomType.HALLWAY.value,
        "кухня": RoomType.KITCHEN.value,
        "kitchen": RoomType.KITCHEN.value,
        "комната": RoomType.ROOM.value,
        "зал": RoomType.ROOM.value,
        "room": RoomType.ROOM.value,
        "ванная": RoomType.BATHROOM.value,
        "bathroom": RoomType.BATHROOM.value,
        "туалет": RoomType.TOILET.value.value,
        "toilet": RoomType.TOILET.value,
        "весь": RoomType.ALL.value,
        "all": RoomType.ALL.value,
        "все": RoomType.ALL.value,
    }
    
    # TV action mapping
    TV_ACTION_MAPPING = {
        "включить": TVAction.ON.value,
        "on": TVAction.ON.value,
        "выключить": TVAction.OFF.value,
        "off": TVAction.OFF.value,
        "нетфликс": TVAction.NETFLIX.value,
        "netflix": TVAction.NETFLIX.value,
        "ютуб": TVAction.YOUTUBE.value,
        "youtube": TVAction.YOUTUBE.value,
        "громче": TVAction.VOLUME_UP.value,
        "volume_up": TVAction.VOLUME_UP.value,
        "тише": TVAction.VOLUME_DOWN.value,
        "volume_down": TVAction.VOLUME_DOWN.value,
    }
    
    # Vacuum action mapping
    VACUUM_ACTION_MAPPING = {
        "начать": VacuumAction.START.value,
        "start": VacuumAction.START.value,
        "уборку": VacuumAction.START.value,
        "убраться": VacuumAction.START.value,
        "база": VacuumAction.DOCK.value,
        "dock": VacuumAction.DOCK.value,
        "домой": VacuumAction.DOCK.value,
        "статус": VacuumAction.STATUS.value,
        "status": VacuumAction.STATUS.value,
        "пауза": VacuumAction.PAUSE.value,
        "pause": VacuumAction.PAUSE.value,
    }
    
    @classmethod
    def validate_room(cls, room: str) -> Optional[str]:
        """Validate and normalize room name"""
        if not room:
            return None
        
        room_lower = room.lower().strip()
        return cls.ROOM_MAPPING.get(room_lower)
    
    @classmethod
    def validate_tv_action(cls, action: str) -> Optional[str]:
        """Validate and normalize TV action"""
        if not action:
            return None
        
        action_lower = action.lower().strip()
        return cls.TV_ACTION_MAPPING.get(action_lower)
    
    @classmethod
    def validate_vacuum_action(cls, action: str) -> Optional[str]:
        """Validate and normalize vacuum action"""
        if not action:
            return None
        
        action_lower = action.lower().strip()
        return cls.VACUUM_ACTION_MAPPING.get(action_lower)
    
    @classmethod
    def validate_brightness(cls, brightness: str) -> Optional[int]:
        """Validate brightness percentage"""
        try:
            # Remove % sign if present
            brightness_clean = brightness.replace('%', '').strip()
            value = int(brightness_clean)
            
            if 0 <= value <= 100:
                return value
            return None
        except (ValueError, AttributeError):
            return None
    
    @classmethod
    def validate_volume(cls, volume: str) -> Optional[int]:
        """Validate volume level"""
        try:
            value = int(volume.strip())
            if 0 <= value <= 100:
                return value
            return None
        except (ValueError, AttributeError):
            return None
    
    @classmethod
    def validate_ip_address(cls, ip: str) -> bool:
        """Validate IP address format"""
        pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(pattern, ip):
            return False
        
        # Check each octet is valid
        octets = ip.split('.')
        return all(0 <= int(octet) <= 255 for octet in octets)
    
    @classmethod
    def validate_token(cls, token: str) -> bool:
        """Validate token format (basic check)"""
        if not token or len(token) < 20:
            return False
        
        # Basic token pattern check
        return bool(re.match(r'^[a-zA-Z0-9:_-]+$', token))


class NaturalLanguageProcessor:
    """Natural language processor for voice/text commands"""
    
    @classmethod
    def parse_light_command(cls, text: str) -> Dict[str, Any]:
        """Parse light control command"""
        text_lower = text.lower()
        
        # Determine action (on/off)
        action = None
        if any(word in text_lower for word in ["включи", "включить", "on", "включен"]):
            action = "on"
        elif any(word in text_lower for word in ["выключи", "выключить", "off", "выключен"]):
            action = "off"
        
        # Find room
        room = None
        for room_name, room_key in CommandValidator.ROOM_MAPPING.items():
            if room_name in text_lower:
                room = room_key
                break
        
        # Find brightness
        brightness = None
        brightness_match = re.search(r'(\d+)%', text)
        if brightness_match:
            brightness = CommandValidator.validate_brightness(brightness_match.group(1))
        
        return {
            "action": action,
            "room": room,
            "brightness": brightness,
            "device_type": DeviceType.LIGHT.value
        }
    
    @classmethod
    def parse_tv_command(cls, text: str) -> Dict[str, Any]:
        """Parse TV control command"""
        text_lower = text.lower()
        
        # Find action
        action = None
        for action_name, action_key in CommandValidator.TV_ACTION_MAPPING.items():
            if action_name in text_lower:
                action = action_key
                break
        
        return {
            "action": action,
            "device_type": DeviceType.TV.value
        }
    
    @classmethod
    def parse_vacuum_command(cls, text: str) -> Dict[str, Any]:
        """Parse vacuum control command"""
        text_lower = text.lower()
        
        # Find action
        action = None
        for action_name, action_key in CommandValidator.VACUUM_ACTION_MAPPING.items():
            if action_name in text_lower:
                action = action_key
                break
        
        return {
            "action": action,
            "device_type": DeviceType.VACUUM.value
        }
    
    @classmethod
    def parse_status_command(cls, text: str) -> Dict[str, Any]:
        """Parse status request command"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["статус", "status", "состояние"]):
            return {"device_type": "status"}
        
        return {}
    
    @classmethod
    def parse_command(cls, text: str) -> Dict[str, Any]:
        """Parse any command and return structured data"""
        text = text.strip()
        
        # Try different command types
        if any(word in text.lower() for word in ["свет", "light"]):
            return cls.parse_light_command(text)
        elif any(word in text.lower() for word in ["телевизор", "tv", "телек"]):
            return cls.parse_tv_command(text)
        elif any(word in text.lower() for word in ["пылесос", "vacuum", "робот"]):
            return cls.parse_vacuum_command(text)
        elif any(word in text.lower() for word in ["статус", "status", "состояние"]):
            return cls.parse_status_command(text)
        
        return {}
