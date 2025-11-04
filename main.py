import os
import subprocess
import psutil
import json
import time
import queue
import sounddevice as sd
import numpy as np
from vosk import Model, KaldiRecognizer
import sys
import signal
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/opencode.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('OpenCode')

class OpenCodeAssistant:
    def __init__(self):
        self.running = False
        self.model = None
        self.rec = None
        self.q = queue.Queue()
        self.setup_signal_handlers()
        
    def setup_signal_handlers(self):
        """Handle graceful shutdown"""
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)
    
    def shutdown(self, signum=None, frame=None):
        """Graceful shutdown handler"""
        logger.info("Shutting down OpenCode...")
        self.speak("Shutting down. Goodbye.")
        self.running = False
        sys.exit(0)

    def speak(self, text):
        """Text-to-speech using Piper"""
        logger.info(f"[OpenCode]: {text}")
        print(f"[OpenCode]: {text}")
        
        try:
            # Generate speech with Piper
            result = subprocess.run([
                "piper",
                "--model", "/models/en_US-libritts_r-medium.onnx",
                "--output_file", "/tmp/speech.wav"
            ], input=text.encode(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
            
            if result.returncode == 0:
                # Play audio
                subprocess.run(["aplay", "/tmp/speech.wav"], 
                             stdout=subprocess.DEVNULL, 
                             stderr=subprocess.DEVNULL,
                             timeout=10)
        except Exception as e:
            logger.error(f"TTS Error: {e}")

    def load_vosk_model(self):
        """Load Vosk speech recognition model"""
        logger.info("Loading Vosk model...")
        model_path = os.getenv("VOSK_MODEL_PATH", "/models/vosk")
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Vosk model not found at {model_path}")
        
        self.model = Model(model_path)
        self.rec = KaldiRecognizer(self.model, 16000)
        logger.info("Vosk model loaded successfully")

    def audio_callback(self, indata, frames, time_info, status):
        """Callback for audio stream"""
        if status:
            logger.warning(f"Audio status: {status}")
        self.q.put(bytes(indata))

    # === System Intelligence Commands ===
    
    def get_system_status(self):
        """Get current system resource usage"""
        try:
            cpu = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory().percent
            disk = psutil.disk_usage("/").percent
            temp = self.get_cpu_temp()
            
            status = f"CPU {cpu}%, Memory {mem}%, Disk {disk}%"
            if temp:
                status += f", Temperature {temp}°C"
            
            return status
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return "Unable to retrieve system status."

    def get_cpu_temp(self):
        """Get CPU temperature if available"""
        try:
            temps = psutil.sensors_temperatures()
            if 'coretemp' in temps:
                return round(temps['coretemp'][0].current, 1)
        except:
            pass
        return None

    def get_network_status(self):
        """Check network connectivity"""
        try:
            output = subprocess.check_output(["ip", "addr"], text=True, timeout=5)
            interfaces = []
            
            for line in output.split('\n'):
                if 'inet ' in line and '127.0.0.1' not in line:
                    interfaces.append(line.strip())
            
            if interfaces:
                return f"Network active. {len(interfaces)} interface(s) connected."
            return "No active network connections found."
        except Exception as e:
            logger.error(f"Network check error: {e}")
            return "Unable to query network status."

    def list_docker_containers(self):
        """List running Docker containers"""
        try:
            output = subprocess.check_output(
                ["docker", "ps", "--format", "{{.Names}} - {{.Status}}"], 
                text=True, 
                timeout=5
            )
            containers = output.strip().split("\n")
            
            if not containers or containers == ['']:
                return "No active Docker containers."
            
            return f"Running containers: {len(containers)}. " + ", ".join(containers[:3])
        except subprocess.CalledProcessError:
            return "Docker not available or permission denied."
        except Exception as e:
            logger.error(f"Docker query error: {e}")
            return "Unable to query Docker containers."

    def manage_container(self, action, container_name):
        """Manage Docker container (start/stop/restart)"""
        try:
            subprocess.run(["docker", action, container_name], 
                         check=True, timeout=30)
            return f"Container {container_name} {action}ed successfully."
        except subprocess.CalledProcessError:
            return f"Failed to {action} container {container_name}."
        except Exception as e:
            logger.error(f"Container management error: {e}")
            return f"Error managing container."

    def run_diagnostics(self):
        """Run system diagnostics"""
        script = "/app/diagnostics.py"
        if os.path.exists(script):
            try:
                subprocess.run(["python3", script], timeout=60)
                return "Diagnostics completed successfully."
            except Exception as e:
                logger.error(f"Diagnostics error: {e}")
                return "Diagnostics failed."
        return "Diagnostics script not found."

    def get_time(self):
        """Get current time"""
        now = datetime.now()
        return now.strftime("The time is %I:%M %p")

    def get_date(self):
        """Get current date"""
        now = datetime.now()
        return now.strftime("Today is %A, %B %d, %Y")

    # === Command Router ===
    
    def handle_command(self, text):
        """Process voice commands"""
        text = text.lower().strip()
        logger.info(f"Processing command: {text}")

        # Browser
        if "open browser" in text:
            os.system("xdg-open https://google.com &")
            self.speak("Opening browser.")
        
        # Time and Date
        elif "what time" in text or "current time" in text:
            self.speak(self.get_time())
        
        elif "what date" in text or "today's date" in text:
            self.speak(self.get_date())
        
        # Diagnostics
        elif "run diagnostics" in text or "diagnose" in text:
            msg = self.run_diagnostics()
            self.speak(msg)

        # System status
        elif "system status" in text or "check system" in text:
            self.speak(self.get_system_status())

        # Network
        elif "network status" in text or "check network" in text:
            self.speak(self.get_network_status())

        # Docker
        elif "list containers" in text or "docker status" in text:
            self.speak(self.list_docker_containers())

        elif "restart container" in text:
            words = text.split()
            if len(words) > 2:
                name = words[-1]
                self.speak(self.manage_container("restart", name))
            else:
                self.speak("Please specify which container to restart.")

        elif "stop container" in text:
            words = text.split()
            if len(words) > 2:
                name = words[-1]
                self.speak(self.manage_container("stop", name))
            else:
                self.speak("Please specify which container to stop.")

        elif "start container" in text:
            words = text.split()
            if len(words) > 2:
                name = words[-1]
                self.speak(self.manage_container("start", name))
            else:
                self.speak("Please specify which container to start.")

        # Help
        elif "help" in text or "what can you do" in text:
            self.speak("I can check system status, network status, list Docker containers, "
                      "manage containers, run diagnostics, tell time and date, or open a browser.")

        # Exit
        elif "shutdown opencode" in text or "stop listening" in text or "exit" in text:
            self.shutdown()

        # Unknown
        else:
            self.speak("Command not recognized. Say help for available commands.")

    # === Wake Word Detection ===
    
    def listen_for_wakeword(self):
        """Listen for wake word activation"""
        logger.info("Listening for wake word...")
        
        while self.running:
            try:
                data = self.q.get(timeout=1)
                if self.rec.AcceptWaveform(data):
                    result = json.loads(self.rec.Result())
                    text = result.get("text", "").lower()
                    
                    if "hey opencode" in text or "hey open code" in text:
                        logger.info("Wake word detected!")
                        self.speak("Yes?")
                        return True
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Wake word detection error: {e}")
        
        return False

    def listen_for_command(self):
        """Listen for command after wake word"""
        logger.info("Listening for command...")
        timeout = time.time() + 10  # 10 second timeout
        
        while self.running and time.time() < timeout:
            try:
                data = self.q.get(timeout=1)
                if self.rec.AcceptWaveform(data):
                    result = json.loads(self.rec.Result())
                    text = result.get("text", "").strip()
                    
                    if text:
                        logger.info(f"[User]: {text}")
                        return text
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Command listening error: {e}")
                break
        
        return None

    # === Main Loop ===
    
    def run(self):
        """Main execution loop"""
        try:
            self.load_vosk_model()
            self.running = True
            
            self.speak("OpenCode is online and ready.")
            logger.info("OpenCode started successfully")
            
            with sd.RawInputStream(
                samplerate=16000, 
                blocksize=8000, 
                dtype='int16',
                channels=1, 
                callback=self.audio_callback
            ):
                while self.running:
                    # Wait for wake word
                    if self.listen_for_wakeword():
                        # Listen for command
                        command = self.listen_for_command()
                        
                        if command:
                            self.handle_command(command)
                        else:
                            self.speak("I didn't catch that.")
                    
                    time.sleep(0.1)
                    
        except KeyboardInterrupt:
            self.shutdown()
        except Exception as e:
            logger.error(f"Fatal error: {e}", exc_info=True)
            self.speak("Critical error occurred. Shutting down.")
            sys.exit(1)


if __name__ == "__main__":
    assistant = OpenCodeAssistant()
    assistant.run()
