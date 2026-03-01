"""Device manager for coordinating all devices"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from .base_device import BaseDevice
from .light_controller import XiaomiLightController
from .tv_controller import AndroidTVController
from .vacuum_controller import XiaomiVacuumController
from config.logging_config import logger


class DeviceManager:
    """Manager for all smart home devices"""
    
    def __init__(self):
        self.devices: Dict[str, BaseDevice] = {}
        self._initialize_devices()
    
    def _initialize_devices(self):
        """Initialize all device controllers"""
        try:
            self.devices["lights"] = XiaomiLightController()
            self.devices["tv"] = AndroidTVController()
            self.devices["vacuum"] = XiaomiVacuumController()
            
            logger.info("Device controllers initialized")
            
        except Exception as e:
            logger.error(f"Error initializing device controllers: {e}")
    
    async def connect_all(self) -> Dict[str, bool]:
        """Connect to all devices"""
        results = {}
        tasks = []
        
        for device_name, device in self.devices.items():
            task = asyncio.create_task(device.connect())
            tasks.append((device_name, task))
        
        for device_name, task in tasks:
            try:
                result = await task
                results[device_name] = result
                if result:
                    logger.info(f"Connected to {device_name}")
                else:
                    logger.warning(f"Failed to connect to {device_name}")
            except Exception as e:
                logger.error(f"Error connecting to {device_name}: {e}")
                results[device_name] = False
        
        return results
    
    async def disconnect_all(self) -> Dict[str, bool]:
        """Disconnect from all devices"""
        results = {}
        tasks = []
        
        for device_name, device in self.devices.items():
            task = asyncio.create_task(device.disconnect())
            tasks.append((device_name, task))
        
        for device_name, task in tasks:
            try:
                result = await task
                results[device_name] = result
                if result:
                    logger.info(f"Disconnected from {device_name}")
                else:
                    logger.warning(f"Failed to disconnect from {device_name}")
            except Exception as e:
                logger.error(f"Error disconnecting from {device_name}: {e}")
                results[device_name] = False
        
        return results
    
    async def get_all_status(self) -> Dict[str, Any]:
        """Get status of all devices"""
        status = {}
        tasks = []
        
        for device_name, device in self.devices.items():
            task = asyncio.create_task(device.get_status())
            tasks.append((device_name, task))
        
        for device_name, task in tasks:
            try:
                result = await task
                status[device_name] = result
            except Exception as e:
                logger.error(f"Error getting status for {device_name}: {e}")
                status[device_name] = {"error": str(e), "online": False}
        
        return status
    
    async def execute_device_command(self, device_type: str, command: str, params: Dict[str, Any] = None) -> bool:
        """Execute command on specific device"""
        try:
            if device_type not in self.devices:
                logger.error(f"Unknown device type: {device_type}")
                return False
            
            device = self.devices[device_type]
            result = await device.safe_execute(command, params)
            
            if result:
                logger.info(f"Command '{command}' executed successfully on {device_type}")
            else:
                logger.warning(f"Command '{command}' failed on {device_type}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing command on {device_type}: {e}")
            return False
    
    async def ping_all_devices(self) -> Dict[str, bool]:
        """Ping all devices to check connectivity"""
        results = {}
        tasks = []
        
        for device_name, device in self.devices.items():
            task = asyncio.create_task(device.ping())
            tasks.append((device_name, task))
        
        for device_name, task in tasks:
            try:
                result = await task
                results[device_name] = result
            except Exception as e:
                logger.error(f"Error pinging {device_name}: {e}")
                results[device_name] = False
        
        return results
    
    def get_device_info(self, device_type: str) -> Optional[Dict[str, Any]]:
        """Get device information"""
        if device_type not in self.devices:
            return None
        
        return self.devices[device_type].get_device_info()
    
    def get_all_device_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all devices"""
        info = {}
        for device_name, device in self.devices.items():
            info[device_name] = device.get_device_info()
        return info
    
    # Light control methods
    async def toggle_light(self, room: str, state: bool) -> bool:
        """Toggle light in specific room"""
        return await self.execute_device_command("lights", "toggle", {"room": room, "state": state})
    
    async def set_light_brightness(self, room: str, brightness: int) -> bool:
        """Set light brightness"""
        return await self.execute_device_command("lights", "set_brightness", {"room": room, "brightness": brightness})
    
    async def toggle_all_lights(self, state: bool) -> bool:
        """Toggle all lights"""
        return await self.execute_device_command("lights", "toggle_all", {"state": state})
    
    # TV control methods
    async def toggle_tv(self, state: bool) -> bool:
        """Toggle TV power"""
        command = "on" if state else "off"
        return await self.execute_device_command("tv", command)
    
    async def launch_tv_app(self, app: str) -> bool:
        """Launch app on TV"""
        return await self.execute_device_command("tv", "launch_app", {"app": app})
    
    async def control_tv_volume(self, action: str) -> bool:
        """Control TV volume"""
        return await self.execute_device_command("tv", "volume", {"action": action})
    
    # Vacuum control methods
    async def start_vacuum(self) -> bool:
        """Start vacuum cleaning"""
        return await self.execute_device_command("vacuum", "start")
    
    async def pause_vacuum(self) -> bool:
        """Pause vacuum cleaning"""
        return await self.execute_device_command("vacuum", "pause")
    
    async def stop_vacuum(self) -> bool:
        """Stop vacuum cleaning"""
        return await self.execute_device_command("vacuum", "stop")
    
    async def dock_vacuum(self) -> bool:
        """Return vacuum to dock"""
        return await self.execute_device_command("vacuum", "dock")
    
    async def set_vacuum_power(self, power: int) -> bool:
        """Set vacuum fan power"""
        return await self.execute_device_command("vacuum", "set_fan_power", {"power": power})
    
    async def find_vacuum(self) -> bool:
        """Make vacuum play sound"""
        return await self.execute_device_command("vacuum", "find")
    
    def get_device_controller(self, device_type: str) -> Optional[BaseDevice]:
        """Get specific device controller"""
        return self.devices.get(device_type)
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all devices"""
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "devices": {},
            "overall_status": "healthy"
        }
        
        # Ping all devices
        ping_results = await self.ping_all_devices()
        
        # Get device info
        device_info = self.get_all_device_info()
        
        for device_name in self.devices.keys():
            is_online = ping_results.get(device_name, False)
            info = device_info.get(device_name, {})
            
            device_health = {
                "online": is_online,
                "last_error": info.get("last_error"),
                "status": "healthy" if is_online else "offline"
            }
            
            health_status["devices"][device_name] = device_health
            
            # Update overall status
            if not is_online:
                health_status["overall_status"] = "degraded"
        
        return health_status


# Global device manager instance
device_manager = DeviceManager()
