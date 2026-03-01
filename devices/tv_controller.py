"""TV controller for Android TV (Kiwi 2K)"""

import asyncio
import subprocess
import socket
from typing import Dict, Any, Optional
from datetime import datetime

from .base_device import BaseDevice
from config.settings import settings
from config.logging_config import logger
from utils.validators import TVAction


class AndroidTVController(BaseDevice):
    """Controller for Android TV via ADB"""
    
    def __init__(self):
        super().__init__("Android TV", "android_tv")
        self.tv_ip = settings.TV_IP_ADDRESS
        self.tv_port = settings.TV_PORT
        self.is_connected = False
        self.tv_status = {
            "on": False,
            "current_app": None,
            "volume": 50,
            "last_updated": datetime.now().isoformat()
        }
    
    async def connect(self) -> bool:
        """Connect to Android TV via ADB"""
        try:
            # Test if TV is reachable
            if not await self._test_connection():
                self.logger.error(f"TV at {self.tv_ip} is not reachable")
                return False
            
            # Connect via ADB
            result = await self._run_adb_command(f"connect {self.tv_ip}:{self.tv_port}")
            if "connected" in result.lower():
                self.is_connected = True
                self.logger.info(f"Connected to Android TV at {self.tv_ip}")
                return True
            else:
                self.logger.error(f"Failed to connect to TV: {result}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error connecting to Android TV: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from Android TV"""
        try:
            if self.is_connected:
                await self._run_adb_command(f"disconnect {self.tv_ip}:{self.tv_port}")
                self.is_connected = False
                self.logger.info("Disconnected from Android TV")
            return True
        except Exception as e:
            self.logger.error(f"Error disconnecting from Android TV: {e}")
            return False
    
    async def get_status(self) -> Dict[str, Any]:
        """Get TV status"""
        try:
            if not self.is_connected:
                await self.connect()
            
            # Check if TV is on by checking if we can get device state
            try:
                result = await self._run_adb_command("shell dumpsys power | grep 'Display Power'")
                self.tv_status["on"] = "ON" in result
            except:
                self.tv_status["on"] = False
            
            # Get current app if TV is on
            if self.tv_status["on"]:
                try:
                    result = await self._run_adb_command("shell dumpsys window windows | grep -E 'mCurrentFocus'")
                    if "mCurrentFocus" in result:
                        # Extract app name from result
                        self.tv_status["current_app"] = self._parse_current_app(result)
                except:
                    self.tv_status["current_app"] = None
            
            self.tv_status["last_updated"] = datetime.now().isoformat()
            return self.tv_status
            
        except Exception as e:
            self.logger.error(f"Error getting TV status: {e}")
            raise
    
    async def execute_command(self, command: str, params: Dict[str, Any] = None) -> bool:
        """Execute TV command"""
        try:
            if command == "power":
                return await self.toggle_power()
            elif command == "on":
                return await self.turn_on()
            elif command == "off":
                return await self.turn_off()
            elif command == "launch_app":
                app = params.get("app")
                return await self.launch_app(app)
            elif command == "volume":
                action = params.get("action")
                return await self.control_volume(action)
            elif command == "input_key":
                key = params.get("key")
                return await self.send_key_event(key)
            else:
                self.logger.error(f"Unknown TV command: {command}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error executing TV command '{command}': {e}")
            return False
    
    async def toggle_power(self) -> bool:
        """Toggle TV power"""
        try:
            await self._run_adb_command("shell input keyevent KEYCODE_POWER")
            self.tv_status["on"] = not self.tv_status["on"]
            self.logger.info(f"TV power toggled, now {'on' if self.tv_status['on'] else 'off'}")
            return True
        except Exception as e:
            self.logger.error(f"Error toggling TV power: {e}")
            return False
    
    async def turn_on(self) -> bool:
        """Turn TV on"""
        try:
            if not self.tv_status["on"]:
                await self._run_adb_command("shell input keyevent KEYCODE_POWER")
                self.tv_status["on"] = True
                self.logger.info("TV turned on")
            return True
        except Exception as e:
            self.logger.error(f"Error turning TV on: {e}")
            return False
    
    async def turn_off(self) -> bool:
        """Turn TV off"""
        try:
            if self.tv_status["on"]:
                await self._run_adb_command("shell input keyevent KEYCODE_POWER")
                self.tv_status["on"] = False
                self.tv_status["current_app"] = None
                self.logger.info("TV turned off")
            return True
        except Exception as e:
            self.logger.error(f"Error turning TV off: {e}")
            return False
    
    async def launch_app(self, app: str) -> bool:
        """Launch app on TV"""
        try:
            if not self.tv_status["on"]:
                await self.turn_on()
            
            app_packages = {
                TVAction.NETFLIX.value: "com.netflix.mediaclient",
                TVAction.YOUTUBE.value: "com.google.android.youtube",
                "youtube": "com.google.android.youtube",
                "netflix": "com.netflix.mediaclient"
            }
            
            package = app_packages.get(app.lower())
            if not package:
                self.logger.error(f"Unknown app: {app}")
                return False
            
            await self._run_adb_command(f"shell monkey -p {package} -c android.intent.category.LAUNCHER 1")
            self.tv_status["current_app"] = app
            self.logger.info(f"Launched {app} on TV")
            return True
            
        except Exception as e:
            self.logger.error(f"Error launching app {app}: {e}")
            return False
    
    async def control_volume(self, action: str) -> bool:
        """Control TV volume"""
        try:
            if not self.tv_status["on"]:
                self.logger.warning("TV is off, cannot control volume")
                return False
            
            if action == "up":
                await self._run_adb_command("shell input keyevent KEYCODE_VOLUME_UP")
                self.tv_status["volume"] = min(100, self.tv_status["volume"] + 5)
            elif action == "down":
                await self._run_adb_command("shell input keyevent KEYCODE_VOLUME_DOWN")
                self.tv_status["volume"] = max(0, self.tv_status["volume"] - 5)
            elif action.isdigit():
                volume = int(action)
                # For setting specific volume, we'd need to use audio manager
                await self._run_adb_command(f"shell service call audio 3 i32 {volume}")
                self.tv_status["volume"] = volume
            else:
                self.logger.error(f"Unknown volume action: {action}")
                return False
            
            self.logger.info(f"TV volume {action}, now at {self.tv_status['volume']}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error controlling TV volume: {e}")
            return False
    
    async def send_key_event(self, key: str) -> bool:
        """Send key event to TV"""
        try:
            key_codes = {
                "home": "KEYCODE_HOME",
                "back": "KEYCODE_BACK",
                "menu": "KEYCODE_MENU",
                "enter": "KEYCODE_ENTER",
                "up": "KEYCODE_DPAD_UP",
                "down": "KEYCODE_DPAD_DOWN",
                "left": "KEYCODE_DPAD_LEFT",
                "right": "KEYCODE_DPAD_RIGHT"
            }
            
            key_code = key_codes.get(key.lower())
            if not key_code:
                self.logger.error(f"Unknown key: {key}")
                return False
            
            await self._run_adb_command(f"shell input keyevent {key_code}")
            self.logger.info(f"Sent key event {key_code} to TV")
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending key event {key}: {e}")
            return False
    
    async def _test_connection(self) -> bool:
        """Test if TV is reachable"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((self.tv_ip, self.tv_port))
            sock.close()
            return result == 0
        except:
            return False
    
    async def _run_adb_command(self, command: str) -> str:
        """Run ADB command"""
        try:
            # Run ADB command asynchronously
            process = await asyncio.create_subprocess_shell(
                f"adb {command}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise Exception(f"ADB command failed: {stderr.decode()}")
            
            return stdout.decode().strip()
            
        except Exception as e:
            self.logger.error(f"Error running ADB command '{command}': {e}")
            raise
    
    def _parse_current_app(self, dumpsys_output: str) -> Optional[str]:
        """Parse current app from dumpsys output"""
        try:
            # Simple parsing - in real implementation would be more robust
            if "netflix" in dumpsys_output.lower():
                return "netflix"
            elif "youtube" in dumpsys_output.lower():
                return "youtube"
            else:
                return "unknown"
        except:
            return None
