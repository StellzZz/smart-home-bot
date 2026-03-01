"""Light controller for Xiaomi Smart Lights"""

import asyncio
import aiohttp
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from .base_device import BaseDevice
from config.settings import settings
from config.logging_config import logger
from utils.validators import RoomType


class XiaomiLightController(BaseDevice):
    """Controller for Xiaomi Smart Lights via Gateway"""
    
    def __init__(self):
        super().__init__("Xiaomi Lights", "xiaomi_lights")
        self.gateway_ip = settings.LIGHT_GATEWAY_IP
        self.gateway_token = None  # Would be set from environment
        self.session = None
        self.lights = {
            RoomType.HALLWAY.value: {"status": False, "brightness": 100, "device_id": "light_001"},
            RoomType.KITCHEN.value: {"status": False, "brightness": 100, "device_id": "light_002"},
            RoomType.ROOM.value: {"status": False, "brightness": 100, "device_id": "light_003"},
            RoomType.BATHROOM.value: {"status": False, "brightness": 80, "device_id": "light_004"},
            RoomType.TOILET.value: {"status": False, "brightness": 60, "device_id": "light_005"},
        }
    
    async def connect(self) -> bool:
        """Connect to Xiaomi Gateway"""
        try:
            self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10))
            
            # Test connection to gateway
            url = f"http://{self.gateway_ip}/api"
            async with self.session.get(url) as response:
                if response.status == 200:
                    self.logger.info("Connected to Xiaomi Gateway")
                    return True
                else:
                    self.logger.error(f"Failed to connect to gateway: HTTP {response.status}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Error connecting to Xiaomi Gateway: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from Xiaomi Gateway"""
        try:
            if self.session:
                await self.session.close()
                self.session = None
            self.logger.info("Disconnected from Xiaomi Gateway")
            return True
        except Exception as e:
            self.logger.error(f"Error disconnecting from Xiaomi Gateway: {e}")
            return False
    
    async def get_status(self) -> Dict[str, Any]:
        """Get status of all lights"""
        try:
            if not self.session:
                await self.connect()
            
            status = {}
            for room, light_info in self.lights.items():
                # In real implementation, this would query the actual device
                # For now, we return the cached status
                status[room] = {
                    "status": light_info["status"],
                    "brightness": light_info["brightness"],
                    "device_id": light_info["device_id"],
                    "last_updated": datetime.now().isoformat()
                }
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error getting light status: {e}")
            raise
    
    async def execute_command(self, command: str, params: Dict[str, Any] = None) -> bool:
        """Execute light command"""
        try:
            params = params or {}
            
            if command == "toggle":
                room = params.get("room")
                state = params.get("state")
                return await self.toggle_light(room, state)
            elif command == "set_brightness":
                room = params.get("room")
                brightness = params.get("brightness")
                return await self.set_brightness(room, brightness)
            elif command == "toggle_all":
                state = params.get("state")
                return await self.toggle_all_lights(state)
            else:
                self.logger.error(f"Unknown light command: {command}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error executing light command '{command}': {e}")
            return False
    
    async def toggle_light(self, room: str, state: bool) -> bool:
        """Toggle specific light"""
        try:
            if room not in self.lights:
                self.logger.error(f"Unknown room: {room}")
                return False
            
            # Update local state
            self.lights[room]["status"] = state
            
            # In real implementation, send command to Xiaomi Gateway
            # For demo purposes, we simulate the API call
            await self._send_gateway_command(
                device_id=self.lights[room]["device_id"],
                command="power",
                params={"status": "on" if state else "off"}
            )
            
            self.logger.info(f"Light in {room} turned {'on' if state else 'off'}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error toggling light in {room}: {e}")
            return False
    
    async def set_brightness(self, room: str, brightness: int) -> bool:
        """Set light brightness"""
        try:
            if room not in self.lights:
                self.logger.error(f"Unknown room: {room}")
                return False
            
            if not 0 <= brightness <= 100:
                self.logger.error(f"Invalid brightness value: {brightness}")
                return False
            
            # Update local state
            self.lights[room]["brightness"] = brightness
            
            # In real implementation, send command to Xiaomi Gateway
            await self._send_gateway_command(
                device_id=self.lights[room]["device_id"],
                command="brightness",
                params={"value": brightness}
            )
            
            self.logger.info(f"Brightness in {room} set to {brightness}%")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting brightness in {room}: {e}")
            return False
    
    async def toggle_all_lights(self, state: bool) -> bool:
        """Toggle all lights"""
        try:
            tasks = []
            for room in self.lights.keys():
                task = self.toggle_light(room, state)
                tasks.append(task)
            
            # Execute all commands concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Check if all succeeded
            success_count = sum(1 for result in results if result is True)
            total_count = len(results)
            
            self.logger.info(f"Toggled all lights: {success_count}/{total_count} successful")
            return success_count == total_count
            
        except Exception as e:
            self.logger.error(f"Error toggling all lights: {e}")
            return False
    
    async def _send_gateway_command(self, device_id: str, command: str, params: Dict[str, Any]) -> bool:
        """Send command to Xiaomi Gateway"""
        try:
            if not self.session:
                await self.connect()
            
            # In real implementation, this would be the actual Xiaomi Gateway API call
            # For demo purposes, we simulate the call
            url = f"http://{self.gateway_ip}/api/devices/{device_id}/commands"
            
            payload = {
                "command": command,
                "params": params,
                "timestamp": datetime.now().timestamp()
            }
            
            # Simulate API call
            self.logger.debug(f"Sending command to gateway: {payload}")
            
            # Simulate successful response
            await asyncio.sleep(0.1)  # Simulate network delay
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending gateway command: {e}")
            return False
    
    def get_room_status(self, room: str) -> Optional[Dict[str, Any]]:
        """Get status of specific room"""
        if room not in self.lights:
            return None
        
        return {
            "room": room,
            "status": self.lights[room]["status"],
            "brightness": self.lights[room]["brightness"],
            "device_id": self.lights[room]["device_id"]
        }
    
    async def get_all_rooms_status(self) -> Dict[str, Any]:
        """Get status of all rooms"""
        status = {}
        for room in self.lights.keys():
            status[room] = self.get_room_status(room)
        return status
