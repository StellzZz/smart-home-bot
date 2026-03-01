"""Tests for validation utilities"""

import pytest
from utils.validators import CommandValidator, NaturalLanguageProcessor, RoomType, DeviceType, TVAction, VacuumAction


class TestCommandValidator:
    """Test CommandValidator class"""
    
    def test_validate_room(self):
        """Test room validation"""
        # Test valid rooms
        assert CommandValidator.validate_room("прихожая") == RoomType.HALLWAY.value
        assert CommandValidator.validate_room("kitchen") == RoomType.KITCHEN.value
        assert CommandValidator.validate_room("комната") == RoomType.ROOM.value
        assert CommandValidator.validate_room("all") == RoomType.ALL.value
        
        # Test invalid rooms
        assert CommandValidator.validate_room("invalid_room") is None
        assert CommandValidator.validate_room("") is None
        assert CommandValidator.validate_room(None) is None
    
    def test_validate_tv_action(self):
        """Test TV action validation"""
        # Test valid actions
        assert CommandValidator.validate_tv_action("включить") == TVAction.ON.value
        assert CommandValidator.validate_tv_action("on") == TVAction.ON.value
        assert CommandValidator.validate_tv_action("netflix") == TVAction.NETFLIX.value
        assert CommandValidator.validate_tv_action("громче") == TVAction.VOLUME_UP.value
        
        # Test invalid actions
        assert CommandValidator.validate_tv_action("invalid_action") is None
        assert CommandValidator.validate_tv_action("") is None
        assert CommandValidator.validate_tv_action(None) is None
    
    def test_validate_vacuum_action(self):
        """Test vacuum action validation"""
        # Test valid actions
        assert CommandValidator.validate_vacuum_action("начать") == VacuumAction.START.value
        assert CommandValidator.validate_vacuum_action("start") == VacuumAction.START.value
        assert CommandValidator.validate_vacuum_action("база") == VacuumAction.DOCK.value
        assert CommandValidator.validate_vacuum_action("статус") == VacuumAction.STATUS.value
        
        # Test invalid actions
        assert CommandValidator.validate_vacuum_action("invalid_action") is None
        assert CommandValidator.validate_vacuum_action("") is None
        assert CommandValidator.validate_vacuum_action(None) is None
    
    def test_validate_brightness(self):
        """Test brightness validation"""
        # Test valid brightness
        assert CommandValidator.validate_brightness("50") == 50
        assert CommandValidator.validate_brightness("75%") == 75
        assert CommandValidator.validate_brightness("0") == 0
        assert CommandValidator.validate_brightness("100") == 100
        
        # Test invalid brightness
        assert CommandValidator.validate_brightness("150") is None
        assert CommandValidator.validate_brightness("-10") is None
        assert CommandValidator.validate_brightness("abc") is None
        assert CommandValidator.validate_brightness("") is None
        assert CommandValidator.validate_brightness(None) is None
    
    def test_validate_volume(self):
        """Test volume validation"""
        # Test valid volume
        assert CommandValidator.validate_volume("50") == 50
        assert CommandValidator.validate_volume("0") == 0
        assert CommandValidator.validate_volume("100") == 100
        
        # Test invalid volume
        assert CommandValidator.validate_volume("150") is None
        assert CommandValidator.validate_volume("-10") is None
        assert CommandValidator.validate_volume("abc") is None
        assert CommandValidator.validate_volume("") is None
        assert CommandValidator.validate_volume(None) is None
    
    def test_validate_ip_address(self):
        """Test IP address validation"""
        # Test valid IPs
        assert CommandValidator.validate_ip_address("192.168.1.100")
        assert CommandValidator.validate_ip_address("127.0.0.1")
        assert CommandValidator.validate_ip_address("10.0.0.1")
        
        # Test invalid IPs
        assert not CommandValidator.validate_ip_address("192.168.1.256")
        assert not CommandValidator.validate_ip_address("192.168.1")
        assert not CommandValidator.validate_ip_address("invalid_ip")
        assert not CommandValidator.validate_ip_address("")
    
    def test_validate_token(self):
        """Test token validation"""
        # Test valid tokens
        assert CommandValidator.validate_token("1234567890:ABCDEF1234567890ABCDEF")
        assert CommandValidator.validate_token("a" * 20)
        
        # Test invalid tokens
        assert not CommandValidator.validate_token("")
        assert not CommandValidator.validate_token("short")
        assert not CommandValidator.validate_token("invalid@token")


class TestNaturalLanguageProcessor:
    """Test NaturalLanguageProcessor class"""
    
    def test_parse_light_command(self):
        """Test light command parsing"""
        # Test turn on commands
        result = NaturalLanguageProcessor.parse_light_command("включи свет в комнате")
        assert result["device_type"] == DeviceType.LIGHT.value
        assert result["action"] == "on"
        assert result["room"] == RoomType.ROOM.value
        
        result = NaturalLanguageProcessor.parse_light_command("выключи свет на кухне")
        assert result["device_type"] == DeviceType.LIGHT.value
        assert result["action"] == "off"
        assert result["room"] == RoomType.KITCHEN.value
        
        # Test brightness command
        result = NaturalLanguageProcessor.parse_light_command("установи яркость 50%")
        assert result["device_type"] == DeviceType.LIGHT.value
        assert result["brightness"] == 50
    
    def test_parse_tv_command(self):
        """Test TV command parsing"""
        # Test TV commands
        result = NaturalLanguageProcessor.parse_tv_command("включи телевизор")
        assert result["device_type"] == DeviceType.TV.value
        assert result["action"] == TVAction.ON.value
        
        result = NaturalLanguageProcessor.parse_tv_command("открой нетфликс")
        assert result["device_type"] == DeviceType.TV.value
        assert result["action"] == TVAction.NETFLIX.value
        
        result = NaturalLanguageProcessor.parse_tv_command("сделай громче")
        assert result["device_type"] == DeviceType.TV.value
        assert result["action"] == TVAction.VOLUME_UP.value
    
    def test_parse_vacuum_command(self):
        """Test vacuum command parsing"""
        # Test vacuum commands
        result = NaturalLanguageProcessor.parse_vacuum_command("начни уборку")
        assert result["device_type"] == DeviceType.VACUUM.value
        assert result["action"] == VacuumAction.START.value
        
        result = NaturalLanguageProcessor.parse_vacuum_command("вернись на базу")
        assert result["device_type"] == DeviceType.VACUUM.value
        assert result["action"] == VacuumAction.DOCK.value
        
        result = NaturalLanguageProcessor.parse_vacuum_command("покажи статус")
        assert result["device_type"] == DeviceType.VACUUM.value
        assert result["action"] == VacuumAction.STATUS.value
    
    def test_parse_status_command(self):
        """Test status command parsing"""
        # Test status commands
        result = NaturalLanguageProcessor.parse_status_command("какой статус")
        assert result["device_type"] == "status"
        
        result = NaturalLanguageProcessor.parse_status_command("покажи состояние")
        assert result["device_type"] == "status"
    
    def test_parse_command_general(self):
        """Test general command parsing"""
        # Test various commands
        result = NaturalLanguageProcessor.parse_command("включи свет")
        assert result["device_type"] == DeviceType.LIGHT.value
        
        result = NaturalLanguageProcessor.parse_command("телевизор")
        assert result["device_type"] == DeviceType.TV.value
        
        result = NaturalLanguageProcessor.parse_command("пылесос")
        assert result["device_type"] == DeviceType.VACUUM.value
        
        result = NaturalLanguageProcessor.parse_command("статус")
        assert result["device_type"] == "status"
        
        # Test unrecognized command
        result = NaturalLanguageProcessor.parse_command("неизвестная команда")
        assert result == {}


if __name__ == "__main__":
    pytest.main([__file__])
