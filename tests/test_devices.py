"""Tests for device controllers"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from devices.base_device import BaseDevice
from devices.light_controller import XiaomiLightController
from devices.tv_controller import AndroidTVController
from devices.vacuum_controller import XiaomiVacuumController
from devices.device_manager import DeviceManager
from utils.validators import RoomType


class MockDevice(BaseDevice):
    """Mock device for testing"""
    
    def __init__(self):
        super().__init__("Mock Device", "mock_device")
        self.connected = False
    
    async def connect(self) -> bool:
        self.connected = True
        return True
    
    async def disconnect(self) -> bool:
        self.connected = False
        return True
    
    async def get_status(self) -> dict:
        return {"status": "online", "connected": self.connected}
    
    async def execute_command(self, command: str, params: dict = None) -> bool:
        return True


class TestBaseDevice:
    """Test BaseDevice class"""
    
    def setup_method(self):
        """Setup test environment"""
        self.device = MockDevice()
    
    def test_device_initialization(self):
        """Test device initialization"""
        assert self.device.name == "Mock Device"
        assert self.device.device_id == "mock_device"
        assert self.device.is_online is True
        assert self.device.last_error is None
    
    @pytest.mark.asyncio
    async def test_connect(self):
        """Test device connection"""
        result = await self.device.connect()
        assert result is True
        assert self.device.connected is True
    
    @pytest.mark.asyncio
    async def test_disconnect(self):
        """Test device disconnection"""
        await self.device.connect()
        result = await self.device.disconnect()
        assert result is True
        assert self.device.connected is False
    
    @pytest.mark.asyncio
    async def test_ping_success(self):
        """Test successful ping"""
        await self.device.connect()
        result = await self.device.ping()
        assert result is True
        assert self.device.is_online is True
    
    @pytest.mark.asyncio
    async def test_ping_failure(self):
        """Test failed ping"""
        # Mock get_status to raise exception
        with patch.object(self.device, 'get_status', side_effect=Exception("Connection failed")):
            result = await self.device.ping()
            assert result is False
            assert self.device.is_online is False
            assert self.device.last_error == "Connection failed"
    
    def test_get_device_info(self):
        """Test device info retrieval"""
        info = self.device.get_device_info()
        assert info["name"] == "Mock Device"
        assert info["device_id"] == "mock_device"
        assert info["is_online"] is True
        assert info["last_error"] is None
    
    @pytest.mark.asyncio
    async def test_safe_execute_success(self):
        """Test safe execute with success"""
        await self.device.connect()
        result = await self.device.safe_execute("test_command")
        assert result is True
    
    @pytest.mark.asyncio
    async def test_safe_execute_failure(self):
        """Test safe execute with failure"""
        # Mock execute_command to raise exception
        with patch.object(self.device, 'execute_command', side_effect=Exception("Command failed")):
            result = await self.device.safe_execute("test_command")
            assert result is False
            assert self.device.is_online is False


class TestXiaomiLightController:
    """Test XiaomiLightController class"""
    
    def setup_method(self):
        """Setup test environment"""
        self.light_controller = XiaomiLightController()
    
    def test_initialization(self):
        """Test controller initialization"""
        assert self.light_controller.name == "Xiaomi Lights"
        assert self.light_controller.device_id == "xiaomi_lights"
        assert RoomType.HALLWAY.value in self.light_controller.lights
        assert self.light_controller.lights[RoomType.HALLWAY.value]["status"] is False
    
    @pytest.mark.asyncio
    async def test_connect(self):
        """Test connection to gateway"""
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = Mock()
            mock_response.status = 200
            mock_get.return_value.__aenter__.return_value = mock_response
            
            result = await self.light_controller.connect()
            assert result is True
            assert self.light_controller.session is not None
    
    @pytest.mark.asyncio
    async def test_toggle_light(self):
        """Test light toggling"""
        # Mock session
        self.light_controller.session = Mock()
        
        # Test turn on
        result = await self.light_controller.toggle_light(RoomType.ROOM.value, True)
        assert result is True
        assert self.light_controller.lights[RoomType.ROOM.value]["status"] is True
        
        # Test turn off
        result = await self.light_controller.toggle_light(RoomType.ROOM.value, False)
        assert result is True
        assert self.light_controller.lights[RoomType.ROOM.value]["status"] is False
    
    @pytest.mark.asyncio
    async def test_toggle_light_invalid_room(self):
        """Test light toggling with invalid room"""
        result = await self.light_controller.toggle_light("invalid_room", True)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_set_brightness(self):
        """Test brightness setting"""
        # Mock session
        self.light_controller.session = Mock()
        
        result = await self.light_controller.set_brightness(RoomType.ROOM.value, 75)
        assert result is True
        assert self.light_controller.lights[RoomType.ROOM.value]["brightness"] == 75
    
    @pytest.mark.asyncio
    async def test_set_brightness_invalid_value(self):
        """Test brightness setting with invalid value"""
        result = await self.light_controller.set_brightness(RoomType.ROOM.value, 150)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_toggle_all_lights(self):
        """Test toggling all lights"""
        # Mock session
        self.light_controller.session = Mock()
        
        # Test turn on all
        result = await self.light_controller.toggle_all_lights(True)
        assert result is True
        
        # Check all lights are on
        for room in self.light_controller.lights.values():
            assert room["status"] is True
        
        # Test turn off all
        result = await self.light_controller.toggle_all_lights(False)
        assert result is True
        
        # Check all lights are off
        for room in self.light_controller.lights.values():
            assert room["status"] is False
    
    def test_get_room_status(self):
        """Test room status retrieval"""
        status = self.light_controller.get_room_status(RoomType.ROOM.value)
        assert status["room"] == RoomType.ROOM.value
        assert "status" in status
        assert "brightness" in status
        assert "device_id" in status
    
    def test_get_room_status_invalid_room(self):
        """Test room status retrieval for invalid room"""
        status = self.light_controller.get_room_status("invalid_room")
        assert status is None


class TestAndroidTVController:
    """Test AndroidTVController class"""
    
    def setup_method(self):
        """Setup test environment"""
        self.tv_controller = AndroidTVController()
    
    def test_initialization(self):
        """Test controller initialization"""
        assert self.tv_controller.name == "Android TV"
        assert self.tv_controller.device_id == "android_tv"
        assert self.tv_controller.tv_status["on"] is False
    
    @pytest.mark.asyncio
    async def test_connect(self):
        """Test connection to TV"""
        with patch.object(self.tv_controller, '_test_connection', return_value=True), \
             patch('asyncio.create_subprocess_shell') as mock_subprocess:
            
            # Mock subprocess
            mock_process = Mock()
            mock_process.communicate.return_value = (b"connected", b"")
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            result = await self.tv_controller.connect()
            assert result is True
            assert self.tv_controller.is_connected is True
    
    @pytest.mark.asyncio
    async def test_toggle_power(self):
        """Test TV power toggle"""
        # Mock connection and subprocess
        self.tv_controller.is_connected = True
        with patch('asyncio.create_subprocess_shell') as mock_subprocess:
            mock_process = Mock()
            mock_process.communicate.return_value = (b"", b"")
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            # Test toggle from off to on
            self.tv_controller.tv_status["on"] = False
            result = await self.tv_controller.toggle_power()
            assert result is True
            assert self.tv_controller.tv_status["on"] is True
    
    @pytest.mark.asyncio
    async def test_turn_on(self):
        """Test turning TV on"""
        # Mock connection and subprocess
        self.tv_controller.is_connected = True
        with patch('asyncio.create_subprocess_shell') as mock_subprocess:
            mock_process = Mock()
            mock_process.communicate.return_value = (b"", b"")
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            result = await self.tv_controller.turn_on()
            assert result is True
            assert self.tv_controller.tv_status["on"] is True
    
    @pytest.mark.asyncio
    async def test_launch_app(self):
        """Test launching app on TV"""
        # Mock connection and subprocess
        self.tv_controller.is_connected = True
        self.tv_controller.tv_status["on"] = True
        with patch('asyncio.create_subprocess_shell') as mock_subprocess:
            mock_process = Mock()
            mock_process.communicate.return_value = (b"", b"")
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            result = await self.tv_controller.launch_app("netflix")
            assert result is True
            assert self.tv_controller.tv_status["current_app"] == "netflix"
    
    @pytest.mark.asyncio
    async def test_control_volume(self):
        """Test volume control"""
        # Mock connection and subprocess
        self.tv_controller.is_connected = True
        self.tv_controller.tv_status["on"] = True
        with patch('asyncio.create_subprocess_shell') as mock_subprocess:
            mock_process = Mock()
            mock_process.communicate.return_value = (b"", b"")
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            # Test volume up
            initial_volume = self.tv_controller.tv_status["volume"]
            result = await self.tv_controller.control_volume("up")
            assert result is True
            assert self.tv_controller.tv_status["volume"] == initial_volume + 5


class TestXiaomiVacuumController:
    """Test XiaomiVacuumController class"""
    
    def setup_method(self):
        """Setup test environment"""
        self.vacuum_controller = XiaomiVacuumController()
    
    def test_initialization(self):
        """Test controller initialization"""
        assert self.vacuum_controller.name == "Xiaomi Vacuum"
        assert self.vacuum_controller.device_id == "xiaomi_vacuum"
        assert self.vacuum_controller.vacuum_status["state"] == "charging"
    
    @pytest.mark.asyncio
    async def test_connect(self):
        """Test connection to vacuum"""
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value = mock_session.return_value
            
            result = await self.vacuum_controller.connect()
            assert result is True
            assert self.vacuum_controller.session is not None
    
    @pytest.mark.asyncio
    async def test_start_cleaning(self):
        """Test starting cleaning"""
        # Mock session
        self.vacuum_controller.session = Mock()
        
        result = await self.vacuum_controller.start_cleaning()
        assert result is True
        assert self.vacuum_controller.vacuum_status["state"] == "cleaning"
    
    @pytest.mark.asyncio
    async def test_pause_cleaning(self):
        """Test pausing cleaning"""
        # Set state to cleaning
        self.vacuum_controller.vacuum_status["state"] = "cleaning"
        self.vacuum_controller.session = Mock()
        
        result = await self.vacuum_controller.pause_cleaning()
        assert result is True
        assert self.vacuum_controller.vacuum_status["state"] == "paused"
    
    @pytest.mark.asyncio
    async def test_return_to_dock(self):
        """Test returning to dock"""
        # Mock session
        self.vacuum_controller.session = Mock()
        
        result = await self.vacuum_controller.return_to_dock()
        assert result is True
        assert self.vacuum_controller.vacuum_status["state"] == "returning"
    
    @pytest.mark.asyncio
    async def test_set_fan_power(self):
        """Test setting fan power"""
        # Mock session
        self.vacuum_controller.session = Mock()
        
        result = await self.vacuum_controller.set_fan_power(75)
        assert result is True
        assert self.vacuum_controller.vacuum_status["fan_power"] == 75
    
    @pytest.mark.asyncio
    async def test_set_fan_power_invalid(self):
        """Test setting invalid fan power"""
        result = await self.vacuum_controller.set_fan_power(150)
        assert result is False
    
    def test_is_low_battery(self):
        """Test low battery check"""
        self.vacuum_controller.vacuum_status["battery"] = 15
        assert self.vacuum_controller.is_low_battery() is True
        
        self.vacuum_controller.vacuum_status["battery"] = 50
        assert self.vacuum_controller.is_low_battery() is False
    
    def test_is_cleaning(self):
        """Test cleaning status check"""
        self.vacuum_controller.vacuum_status["state"] = "cleaning"
        assert self.vacuum_controller.is_cleaning() is True
        
        self.vacuum_controller.vacuum_status["state"] = "charging"
        assert self.vacuum_controller.is_cleaning() is False


class TestDeviceManager:
    """Test DeviceManager class"""
    
    def setup_method(self):
        """Setup test environment"""
        self.device_manager = DeviceManager()
    
    def test_initialization(self):
        """Test manager initialization"""
        assert "lights" in self.device_manager.devices
        assert "tv" in self.device_manager.devices
        assert "vacuum" in self.device_manager.devices
    
    @pytest.mark.asyncio
    async def test_connect_all(self):
        """Test connecting to all devices"""
        # Mock device connections
        for device in self.device_manager.devices.values():
            device.connect = AsyncMock(return_value=True)
        
        results = await self.device_manager.connect_all()
        
        assert all(results.values())
        assert len(results) == 3
    
    @pytest.mark.asyncio
    async def test_disconnect_all(self):
        """Test disconnecting from all devices"""
        # Mock device disconnections
        for device in self.device_manager.devices.values():
            device.disconnect = AsyncMock(return_value=True)
        
        results = await self.device_manager.disconnect_all()
        
        assert all(results.values())
        assert len(results) == 3
    
    @pytest.mark.asyncio
    async def test_execute_device_command(self):
        """Test executing device command"""
        # Mock device command execution
        mock_device = Mock()
        mock_device.safe_execute = AsyncMock(return_value=True)
        self.device_manager.devices["lights"] = mock_device
        
        result = await self.device_manager.execute_device_command("lights", "toggle", {"room": "room", "state": True})
        
        assert result is True
        mock_device.safe_execute.assert_called_once_with("toggle", {"room": "room", "state": True})
    
    @pytest.mark.asyncio
    async def test_execute_device_command_invalid_device(self):
        """Test executing command on invalid device"""
        result = await self.device_manager.execute_device_command("invalid_device", "command")
        assert result is False
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test health check"""
        # Mock device pings
        for device in self.device_manager.devices.values():
            device.ping = AsyncMock(return_value=True)
        
        health = await self.device_manager.health_check()
        
        assert "timestamp" in health
        assert "devices" in health
        assert "overall_status" in health
        assert health["overall_status"] == "healthy"
    
    def test_get_device_info(self):
        """Test getting device info"""
        info = self.device_manager.get_device_info("lights")
        assert info is not None
        assert "name" in info
        assert "device_id" in info
        
        info = self.device_manager.get_device_info("invalid_device")
        assert info is None


if __name__ == "__main__":
    pytest.main([__file__])
