# OpenCode Voice Assistant

A containerized voice-controlled system management assistant built with Python, Vosk, and Piper TTS.

## Features

- 🎤 **Voice Recognition**: Wake word activation ("Hey OpenCode")
- 🔊 **Text-to-Speech**: Natural voice responses using Piper TTS
- 🐳 **Docker Management**: Monitor and control Docker containers
- 💻 **System Monitoring**: CPU, memory, disk, and network status
- 🔧 **Diagnostics**: Comprehensive system health checks
- ⏰ **Time & Date**: Query current time and date
- 🌐 **Browser Control**: Launch web browser

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Microphone and speakers/audio output
- Linux host (for full audio support)

### Installation

1. **Clone or create the project directory**:
```bash
mkdir opencode && cd opencode
```

2. **Create the required files** (copy all the artifacts provided):
   - `main.py`
   - `diagnostics.py`
   - `Dockerfile`
   - `docker-compose.yml`
   - `requirements.txt`
   - `config.json`

3. **Create necessary directories**:
```bash
mkdir -p logs models config
```

4. **Build the Docker image**:
```bash
docker-compose build
```

5. **Run OpenCode**:
```bash
docker-compose up -d
```

6. **View logs**:
```bash
docker-compose logs -f
```

## Usage

### Voice Commands

**System Management:**
- "Hey OpenCode, system status"
- "Hey OpenCode, check network"
- "Hey OpenCode, run diagnostics"

**Docker Management:**
- "Hey OpenCode, list containers"
- "Hey OpenCode, restart container [name]"
- "Hey OpenCode, stop container [name]"
- "Hey OpenCode, start container [name]"

**Utilities:**
- "Hey OpenCode, what time is it?"
- "Hey OpenCode, what's today's date?"
- "Hey OpenCode, open browser"
- "Hey OpenCode, help"

**Control:**
- "Hey OpenCode, shutdown" / "exit" / "stop listening"

### Manual Control

Start the container:
```bash
docker-compose up -d
```

Stop the container:
```bash
docker-compose down
```

Restart:
```bash
docker-compose restart
```

View real-time logs:
```bash
docker-compose logs -f opencode
```

Access container shell:
```bash
docker exec -it opencode-assistant bash
```

## Configuration

Edit `config.json` to customize:
- Wake words
- Audio settings
- Command phrases
- Feature toggles
- Logging preferences

## Troubleshooting

### No Audio Input/Output

**Check audio devices:**
```bash
docker exec opencode-assistant aplay -l
docker exec opencode-assistant arecord -l
```

**Verify PulseAudio:**
```bash
pactl info
```

**Update docker-compose.yml** with correct device paths if needed.

### Docker Permission Issues

Add your user to the docker group:
```bash
sudo usermod -aG docker $USER
newgrp docker
```

### Models Not Downloaded

Download Vosk model manually:
```bash
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip -d ./models
mv ./models/vosk-model-small-en-us-0.15 ./models/vosk
```

Download Piper model:
```bash
wget -O ./models/en_US-libritts_r-medium.onnx \
  https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/libritts/high/en_US-libritts-high.onnx
```

### Container Won't Start

Check logs:
```bash
docker-compose logs opencode
```

Rebuild image:
```bash
docker-compose build --no-cache
docker-compose up -d
```

## Architecture

```
opencode/
├── main.py                 # Main application
├── diagnostics.py          # System diagnostics
├── config.json            # Configuration
├── Dockerfile             # Container definition
├── docker-compose.yml     # Compose configuration
├── requirements.txt       # Python dependencies
├── logs/                  # Application logs
├── models/               # Speech models
│   ├── vosk/            # Vosk speech recognition
│   └── en_US-*.onnx     # Piper TTS model
└── config/              # Additional configs
```

## Development

### Adding New Commands

1. Edit `handle_command()` in `main.py`
2. Add command phrases to `config.json`
3. Restart container

### Changing Wake Word

Edit `config.json`:
```json
{
  "wake_word": {
    "phrases": ["hey assistant", "hello computer"]
  }
}
```

### Custom Diagnostics

Add checks to `diagnostics.py` and call via voice command.

## Performance

**Resource Usage:**
- CPU: ~0.5-1 core during listening
- Memory: ~500MB-1GB
- Disk: ~2GB (including models)

**Optimize by:**
- Using smaller Vosk models
- Adjusting audio buffer sizes
- Limiting container resources in docker-compose.yml

## Security Notes

- Container runs with Docker socket access (for container management)
- Use `privileged: false` if Docker management not needed
- Audio device access requires elevated permissions
- Consider running in isolated network for production

## License

This is a personal project. Modify and use as needed.

## Credits

- **Vosk**: Speech recognition (Apache 2.0)
- **Piper**: Text-to-speech (MIT)
- **Python**: Core language
- **Docker**: Containerization

## Support

For issues or questions:
1. Check logs: `docker-compose logs`
2. Review troubleshooting section
3. Verify audio device permissions
4. Test microphone with `arecord -l`

---

**Version**: 1.0.0  
**Last Updated**: 2025-11-04
