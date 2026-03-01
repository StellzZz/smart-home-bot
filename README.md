# 🏠 Smart Home Jarvis - Production-Ready MVP

**Enterprise-grade smart home assistant with Telegram interface, voice control, and comprehensive device management.**

## 🎯 Features

### 🤖 Core Capabilities
- **Telegram Bot Interface** - Full-featured bot with inline keyboards
- **Voice Command Processing** - Natural language understanding
- **Multi-Device Control** - Lights, TV, vacuum cleaner
- **Real-time Status Monitoring** - Device health and status tracking
- **Production-Ready Architecture** - Scalable, secure, maintainable

### 🗣️ Voice & Text Commands
- **Natural Language Processing** - Understands conversational commands
- **Multi-language Support** - Russian and English
- **Voice Recognition** - Google Speech API integration
- **Text Processing** - Smart command parsing

### 💡 Smart Lighting (Xiaomi)
- **Room-based Control** - Hallway, kitchen, room, bathroom, toilet
- **Brightness Adjustment** - 0-100% dimming
- **Group Operations** - Control all lights simultaneously
- **Real-time Status** - Monitor each light's state

### 📺 TV Control (Android TV/Kiwi 2K)
- **Power Management** - On/off control via ADB
- **App Launching** - Netflix, YouTube, custom apps
- **Volume Control** - Up/down with percentage setting
- **Input Simulation** - Full remote control capabilities

### 🤖 Vacuum Control (Xiaomi X20+)
- **Cleaning Modes** - Start, pause, stop cleaning
- **Dock Management** - Return to base, charge monitoring
- **Status Tracking** - Battery level, cleaning time, area covered
- **Locate Feature** - Audio beacon for finding the vacuum

### 🔒 Security & Safety
- **User Authorization** - Whitelist-based access control
- **Rate Limiting** - Prevent abuse and spam
- **Session Management** - Secure token-based sessions
- **Input Validation** - Comprehensive data validation
- **Error Handling** - Graceful failure recovery
- **Audit Logging** - Security event tracking

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Telegram Bot API                        │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                   FastAPI Web Server                        │
│              + Webhook Support                               │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                   Bot Module                                │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐   │
│  │   Commands  │ │   Handlers  │ │   Voice Processing  │   │
│  └─────────────┘ └─────────────┘ └─────────────────────┘   │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                 Service Layer                               │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐   │
│  │   Auth      │ │ Validation  │ │   Rate Limiting     │   │
│  │   Service   │ │   Service   │ │     Service         │   │
│  └─────────────┘ └─────────────┘ └─────────────────────┘   │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                Device Controller                            │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐   │
│  │   Light     │ │      TV     │ │     Vacuum          │   │
│  │ Controller  │ │ Controller  │ │   Controller       │   │
│  └─────────────┘ └─────────────┘ └─────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Telegram Bot Token
- Smart home devices (optional for testing)

### 1. Installation
```bash
# Clone repository
git clone <repository-url>
cd smart_home_bot

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env
```

### 2. Configuration
Edit `.env` file with your settings:
```bash
# Required
TELEGRAM_TOKEN=your_telegram_bot_token_here
TELEGRAM_USER_IDS=123456789,987654321

# Optional (for device control)
TV_IP_ADDRESS=192.168.1.100
VACUUM_IP_ADDRESS=192.168.1.101
LIGHT_GATEWAY_IP=192.168.1.102
```

### 3. Running the Bot
```bash
# Development mode with polling
python main.py polling

# Production mode with web server
python main.py web

# Webhook mode (requires webhook URL)
python main.py webhook
```

## 📱 Commands Reference

### Basic Commands
| Command | Description |
|---------|-------------|
| `/start` | Initialize bot and show main menu |
| `/help` | Display detailed help information |
| `/status` | Show status of all devices |
| `/health` | System health check |

### Lighting Commands
| Command | Description |
|---------|-------------|
| `/light_on [room]` | Turn on lights in room |
| `/light_off [room]` | Turn off lights in room |
| `/light_brightness [room] [0-100]` | Set brightness (0-100%) |

**Rooms:** `hallway`, `kitchen`, `room`, `bathroom`, `toilet`, `all`

### TV Commands
| Command | Description |
|---------|-------------|
| `/tv_on` | Turn on TV |
| `/tv_off` | Turn off TV |
| `/tv netflix` | Launch Netflix |
| `/tv youtube` | Launch YouTube |
| `/tv_volume up/down` | Adjust volume |

### Vacuum Commands
| Command | Description |
|---------|-------------|
| `/vacuum_start` | Start cleaning |
| `/vacuum_pause` | Pause cleaning |
| `/vacuum_dock` | Return to base |
| `/vacuum_find` | Play locator sound |

### Natural Language Examples
- "Включи свет в комнате" → Turn on room lights
- "Выключи телевизор" → Turn off TV
- "Начни уборку" → Start vacuum cleaning
- "Покажи статус" → Show device status

## 🐳 Docker Deployment

### Simple Deployment
```bash
# Build and run
docker-compose up -d

# Check logs
docker-compose logs -f smart-home-bot
```

### Production Deployment
```bash
# With database and caching
docker-compose --profile database --profile cache up -d

# With nginx reverse proxy
docker-compose --profile production up -d
```

## ☁️ Cloud Deployment

### Render.com
1. **Create Web Service**
   - Connect GitHub repository
   - Use `render.yaml` configuration

2. **Environment Variables**
   - Set all required variables from `.env.example`
   - Configure webhook URL: `https://your-app.onrender.com/webhook`

3. **Deploy**
   - Auto-deployment on git push
   - Health checks enabled

### Manual Cloud Deployment
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export TELEGRAM_TOKEN="your_token"
export TELEGRAM_USER_IDS="your_user_id"

# Run with Gunicorn (production)
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

## 🧪 Testing

### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_validators.py

# Run with verbose output
pytest -v
```

### Test Coverage
- Unit tests for all core components
- Integration tests for device controllers
- Security tests for authentication
- API tests for web endpoints

## 🔧 Configuration

### Security Settings
```python
# User authorization
TELEGRAM_USER_IDS=123456789,987654321
ALLOWED_USERNAMES=username1,username2

# Rate limiting
RATE_LIMIT_REQUESTS=30
RATE_LIMIT_PERIOD=60

# Webhook security
TELEGRAM_WEBHOOK_SECRET=random_secret_string
```

### Device Settings
```python
# Android TV
TV_IP_ADDRESS=192.168.1.100
TV_PORT=5555

# Xiaomi Vacuum
VACUUM_IP_ADDRESS=192.168.1.101
VACUUM_TOKEN=xiaomi_token_here

# Xiaomi Lights
LIGHT_GATEWAY_IP=192.168.1.102
```

### Logging Configuration
```python
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
LOG_FILE=logs/smart_home.log
DEBUG=false
```

## 📊 Monitoring & Health

### Health Endpoints
- `GET /health` - System health check
- `GET /status` - Device status overview
- `GET /security/stats` - Security statistics

### Logging
- **Application Logs** - General system events
- **Security Logs** - Authentication and authorization
- **Error Logs** - System errors and exceptions
- **Device Logs** - Device communication logs

### Metrics
- Device connectivity status
- Command execution success rates
- Response time monitoring
- Security event tracking

## 🔒 Security Features

### Authentication & Authorization
- **User Whitelisting** - Only authorized users
- **Session Management** - Secure token-based sessions
- **Rate Limiting** - Prevent abuse and DoS attacks
- **Input Validation** - Comprehensive data sanitization

### Data Protection
- **Environment Variables** - Sensitive data isolation
- **No Hardcoded Secrets** - All tokens externalized
- **Secure Headers** - HTTP security headers
- **Audit Trail** - Security event logging

### Network Security
- **Webhook Validation** - Secret token verification
- **HTTPS Only** - Encrypted communication
- **IP Filtering** - Optional network restrictions
- **Timeout Protection** - Request timeout enforcement

## 🚀 Scaling & Extensibility

### Adding New Devices
1. **Create Device Controller**
   ```python
   class NewDeviceController(BaseDevice):
       async def connect(self) -> bool: ...
       async def execute_command(self, command: str) -> bool: ...
   ```

2. **Register in Device Manager**
   ```python
   self.devices["new_device"] = NewDeviceController()
   ```

3. **Add Bot Commands**
   ```python
   @authorized_users_only
   async def new_device_command(update, context):
       await device_manager.execute_device_command("new_device", "action")
   ```

### Database Integration
- **SQLite** - Default for development
- **PostgreSQL** - Production scaling
- **Redis** - Caching and session storage
- **Migration Support** - Alembic integration

### API Extensions
- **REST API** - Additional endpoints
- **WebSocket** - Real-time updates
- **GraphQL** - Flexible queries
- **Webhooks** - Event notifications

## 🐛 Troubleshooting

### Common Issues

**Bot doesn't respond:**
- Check `TELEGRAM_TOKEN` is correct
- Verify user ID in `TELEGRAM_USER_IDS`
- Check logs for errors

**Device control not working:**
- Verify device IP addresses
- Check network connectivity
- Review device-specific logs

**Voice recognition fails:**
- Install `SpeechRecognition` package
- Check microphone permissions
- Verify internet connectivity

**Webhook issues:**
- Ensure webhook URL is accessible
- Verify `TELEGRAM_WEBHOOK_SECRET` matches
- Check SSL certificate validity

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
export DEBUG=true

# Run with verbose output
python main.py polling
```

## 📚 API Documentation

### Web API Endpoints

#### Health Check
```http
GET /health
```

#### Device Status
```http
GET /status
Authorization: Bearer <session_token>
```

#### Device Control
```http
POST /device/{device_type}/{command}
Content-Type: application/json

{
  "params": {
    "room": "kitchen",
    "state": true
  }
}
```

#### Security Statistics
```http
GET /security/stats
Authorization: Bearer <admin_token>
```

## 🤝 Contributing

### Development Setup
```bash
# Clone repository
git clone <repository-url>
cd smart_home_bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
pytest

# Code formatting
black .
flake8 .
mypy .
```

### Code Standards
- **PEP 8** - Python style guide
- **Type Hints** - Full type annotation
- **Docstrings** - Comprehensive documentation
- **Tests** - 80%+ coverage requirement

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
1. Check the troubleshooting section
2. Review the logs for error messages
3. Create an issue on GitHub
4. Contact the development team

---

**🏠 Smart Home Jarvis - Your intelligent home assistant, ready for production!**
