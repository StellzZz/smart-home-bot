"""Base device controller class"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import asyncio
import logging

from config.logging_config import logger


class BaseDevice(ABC):
    """Base class for all device controllers"""
    
    def __init__(self, name: str, device_id: str):
        self.name = name
        self.device_id = device_id
        self.is_online = True
        self.last_error = None
        self.logger = logging.getLogger(f"device.{device_id}")
    
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to device"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Disconnect from device"""
        pass
    
    @abstractmethod
    async def get_status(self) -> Dict[str, Any]:
        """Get device status"""
        pass
    
    @abstractmethod
    async def execute_command(self, command: str, params: Dict[str, Any] = None) -> bool:
        """Execute command on device"""
        pass
    
    async def ping(self) -> bool:
        """Check if device is online"""
        try:
            status = await self.get_status()
            self.is_online = True
            return True
        except Exception as e:
            self.logger.error(f"Device {self.name} ping failed: {e}")
            self.is_online = False
            self.last_error = str(e)
            return False
    
    def get_device_info(self) -> Dict[str, Any]:
        """Get device information"""
        return {
            "name": self.name,
            "device_id": self.device_id,
            "is_online": self.is_online,
            "last_error": self.last_error
        }
    
    async def safe_execute(self, command: str, params: Dict[str, Any] = None, timeout: int = 30) -> bool:
        """Safely execute command with timeout and error handling"""
        try:
            if not self.is_online:
                self.logger.warning(f"Device {self.name} is offline, cannot execute command: {command}")
                return False
            
            result = await asyncio.wait_for(
                self.execute_command(command, params),
                timeout=timeout
            )
            
            if result:
                self.logger.info(f"Command '{command}' executed successfully on {self.name}")
            else:
                self.logger.warning(f"Command '{command}' failed on {self.name}")
            
            return result
            
        except asyncio.TimeoutError:
            self.logger.error(f"Command '{command}' timed out on {self.name}")
            self.last_error = f"Command timeout: {command}"
            return False
        except Exception as e:
            self.logger.error(f"Error executing command '{command}' on {self.name}: {e}")
            self.last_error = str(e)
            self.is_online = False
            return False
