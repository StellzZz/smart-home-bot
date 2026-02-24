import os
import asyncio
import json
from datetime import datetime
from typing import Dict, Any

class JarvisAssistant:
    def __init__(self):
        self.name = "Джарвис"
        self.voice_type = "british"  # британский акцент
        self.devices = {
            "lights": {
                "hallway": False,
                "kitchen": False,
                "room": False,
                "bathroom": False,
                "toilet": False
            },
            "tv": {
                "on": False,
                "volume": 50,
                "channel": 1
            },
            "vacuum": {
                "cleaning": False,
                "docked": True,
                "battery": 100
            }
        }
        
    def process_command(self, command: str) -> str:
        """Обработка голосовых команд"""
        command = command.lower().strip()
        
        # Управление светом
        if "включи свет в прихожей" in command:
            return self.toggle_light("hallway", True)
        elif "включи свет на кухне" in command:
            return self.toggle_light("kitchen", True)
        elif "включи свет в комнате" in command:
            return self.toggle_light("room", True)
        elif "включи свет в ванной" in command:
            return self.toggle_light("bathroom", True)
        elif "включи свет в туалете" in command:
            return self.toggle_light("toilet", True)
        elif "выключи свет в прихожей" in command:
            return self.toggle_light("hallway", False)
        elif "выключи свет на кухне" in command:
            return self.toggle_light("kitchen", False)
        elif "выключи свет в комнате" in command:
            return self.toggle_light("room", False)
        elif "выключи свет в ванной" in command:
            return self.toggle_light("bathroom", False)
        elif "выключи свет в туалете" in command:
            return self.toggle_light("toilet", False)
        elif "выключи весь свет" in command:
            return self.toggle_all_lights(False)
        elif "пригласи свет на" in command:
            try:
                percent = int(command.split()[-1].replace("%", ""))
                return self.set_light_brightness(percent)
            except:
                return "Не удалось установить яркость"
        
        # Управление телевизором
        elif "включи телевизор" in command:
            return self.toggle_tv(True)
        elif "включи netflix" in command:
            return self.tv_control("netflix")
        elif "включи youtube" in command:
            return self.tv_control("youtube")
        elif "выключи телевизор" in command:
            return self.toggle_tv(False)
        elif "повысь громкость на" in command:
            try:
                volume = int(command.split()[-1])
                return self.set_volume(volume)
            except:
                return "Не удалось изменить громкость"
        elif "понизь громкость на" in command:
            try:
                volume = int(command.split()[-1])
                return self.set_volume(volume, decrease=True)
            except:
                return "Не удалось изменить громкость"
        elif "установи громкость на" in command:
            try:
                volume = int(command.split()[-1])
                return self.set_volume(volume)
            except:
                return "Не удалось установить громкость"
        
        # Управление пылесосом
        elif "начни уборку" in command:
            return self.start_vacuum()
        elif "вернись на базу" in command:
            return self.dock_vacuum()
        elif "статус пылесоса" in command:
            return self.get_vacuum_status()
        
        # Системные команды
        elif "какой статус устройств" in command:
            return self.get_all_status()
        elif "погода на сегодня" in command:
            return self.get_weather()
        elif "сколько времени" in command:
            return f"Сейчас {datetime.now().strftime('%H:%M')}"
        elif "сколько времени займет дорога до" in command:
            return self.get_traffic_info(command)
        
        return "Команда не распознана"
    
    def toggle_light(self, room: str, state: bool) -> str:
        """Включить/выключить свет в комнате"""
        self.devices["lights"][room] = state
        action = "включён" if state else "выключен"
        return f"Свет в {self.get_room_name(room)} {action}"
    
    def toggle_all_lights(self, state: bool) -> str:
        """Включить/выключить весь свет"""
        for room in self.devices["lights"]:
            self.devices["lights"][room] = state
        action = "включен" if state else "выключен"
        return f"Весь свет {action}"
    
    def set_light_brightness(self, percent: int) -> str:
        """Установить яркость света"""
        if 0 <= percent <= 100:
            return f"Яркость света установлена на {percent}%"
        return "Неверное значение яркости"
    
    def toggle_tv(self, state: bool) -> str:
        """Включить/выключить телевизор"""
        self.devices["tv"]["on"] = state
        action = "включен" if state else "выключен"
        return f"Телевизор {action}"
    
    def tv_control(self, app: str) -> str:
        """Управление приложениями на TV"""
        if self.devices["tv"]["on"]:
            return f"Переключаю на {app}"
        return "Сначала включите телевизор"
    
    def set_volume(self, volume: int, decrease: bool = False) -> str:
        """Установить громкость"""
        if decrease:
            self.devices["tv"]["volume"] = max(0, self.devices["tv"]["volume"] - volume)
        else:
            self.devices["tv"]["volume"] = max(0, min(100, volume))
        
        return f"Громкость установлена на {self.devices['tv']['volume']}"
    
    def start_vacuum(self) -> str:
        """Начать уборку"""
        if not self.devices["vacuum"]["cleaning"]:
            self.devices["vacuum"]["cleaning"] = True
            self.devices["vacuum"]["docked"] = False
            return "Начинаю уборку, сэр"
        return "Уборка уже выполняется"
    
    def dock_vacuum(self) -> str:
        """Вернуть пылесос на базу"""
        self.devices["vacuum"]["cleaning"] = False
        self.devices["vacuum"]["docked"] = True
        return "Возвращаюсь на базу"
    
    def get_vacuum_status(self) -> str:
        """Статус пылесоса"""
        if self.devices["vacuum"]["cleaning"]:
            return "Пылесос выполняет уборку"
        elif self.devices["vacuum"]["docked"]:
            return "Пылесос на базе, заряжен"
        else:
            return f"Пылесос в режиме ожидания, заряд: {self.devices['vacuum']['battery']}%"
    
    def get_room_name(self, room: str) -> str:
        """Получить название комнаты на русском"""
        room_names = {
            "hallway": "прихожей",
            "kitchen": "кухне",
            "room": "комнате",
            "bathroom": "ванной",
            "toilet": "туалете"
        }
        return room_names.get(room, room)
    
    def get_all_status(self) -> str:
        """Статус всех устройств"""
        status = []
        
        # Свет
        lights_on = sum(1 for light in self.devices["lights"].values() if light)
        status.append(f"Свет: {lights_on} из {len(self.devices['lights'])} комнат включено")
        
        # Телевизор
        tv_status = "включен" if self.devices["tv"]["on"] else "выключен"
        status.append(f"Телевизор: {tv_status}")
        
        # Пылесос
        vac_status = self.get_vacuum_status()
        status.append(f"Пылесос: {vac_status}")
        
        return "\n".join(status)
    
    def get_weather(self) -> str:
        """Информация о погоде"""
        return "Погода сегодня: 22°C, облачно, без осадков"
    
    def get_traffic_info(self, command: str) -> str:
        """Информация о пробках"""
        return "Информация о дорогах недоступна, сэр"

# Глобальный экземпляр Джарвиса
jarvis = JarvisAssistant()
