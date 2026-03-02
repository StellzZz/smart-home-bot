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
        "прихожая": RoomType.HALLWAY,
        "коридор": RoomType.HALLWAY,
        "hallway": RoomType.HALLWAY,
        "кухня": RoomType.KITCHEN,
        "kitchen": RoomType.KITCHEN,
        "комната": RoomType.ROOM,
        "зал": RoomType.ROOM,
        "room": RoomType.ROOM,
        "ванная": RoomType.BATHROOM,
        "bathroom": RoomType.BATHROOM,
        "туалет": RoomType.TOILET,
        "toilet": RoomType.TOILET,
        "весь": RoomType.ALL,
        "all": RoomType.ALL,
    }
    
    # TV action mapping
    TV_ACTION_MAPPING = {
        "включить": TVAction.ON,
        "on": TVAction.ON,
        "выключить": TVAction.OFF,
        "off": TVAction.OFF,
        "нетфликс": TVAction.NETFLIX,
        "netflix": TVAction.NETFLIX,
        "ютуб": TVAction.YOUTUBE,
        "youtube": TVAction.YOUTUBE,
        "громче": TVAction.VOLUME_UP,
        "volume_up": TVAction.VOLUME_UP,
        "тише": TVAction.VOLUME_DOWN,
        "volume_down": TVAction.VOLUME_DOWN,
    }
    
    # Vacuum action mapping
    VACUUM_ACTION_MAPPING = {
        "начать": VacuumAction.START,
        "start": VacuumAction.START,
        "уборку": VacuumAction.START,
        "убраться": VacuumAction.START,
        "база": VacuumAction.DOCK,
        "dock": VacuumAction.DOCK,
        "домой": VacuumAction.DOCK,
        "статус": VacuumAction.STATUS,
        "status": VacuumAction.STATUS,
        "пауза": VacuumAction.PAUSE,
        "pause": VacuumAction.PAUSE,
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
