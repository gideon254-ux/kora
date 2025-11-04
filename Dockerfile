FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    alsa-utils \
    libasound2-dev \
    portaudio19-dev \
    python3-pyaudio \
    wget \
    git \
    curl \
    iputils-ping \
    iproute2 \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

# Install Piper TTS
RUN wget https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_amd64.tar.gz \
    && tar -xzf piper_amd64.tar.gz -C /usr/local/bin \
    && rm piper_amd64.tar.gz \
    && chmod +x /usr/local/bin/piper

# Create directories
RUN mkdir -p /app /models/vosk /app/logs /tmp

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY main.py .
COPY diagnostics.py .
COPY config.json .

# Download Vosk model (small English model)
# You can replace this with a larger model for better accuracy
RUN wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip \
    && unzip vosk-model-small-en-us-0.15.zip -d /models \
    && mv /models/vosk-model-small-en-us-0.15 /models/vosk \
    && rm vosk-model-small-en-us-0.15.zip

# Download Piper voice model
RUN mkdir -p /models && \
    wget -O /models/en_US-libritts_r-medium.onnx \
    https://github.com/rhasspy/piper/releases/download/v0.0.2/voice-en-us-libritts-high.tar.gz \
    || echo "Note: Download Piper model manually if this fails"

# Set environment variables
ENV VOSK_MODEL_PATH=/models/vosk
ENV PYTHONUNBUFFERED=1
ENV PULSE_SERVER=unix:/run/user/1000/pulse/native

# Volume for persistent data
VOLUME ["/app/logs"]

# Expose any ports if needed (for future web interface)
EXPOSE 8080

# Run the application
CMD ["python3", "main.py"]
