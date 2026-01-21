#!/usr/bin/env python3
"""
HUD Display - Main Application
Connects to SSE endpoint and displays vehicle speed on various displays:
- TFT35" Touch Shield (default)
- Pico Scroll Pack (via Raspberry Pi Pico)
- Qualia ESP32-S3 RGB666 TFT Display

Set DISPLAY_TYPE environment variable to select display:
  - 'tft' or not set: TFT35" display
  - 'pico' or 'picoscroll': Pico Scroll Pack
  - 'qualia', 'esp32', or 'esp32-s3': Qualia ESP32-S3 RGB666 TFT
"""

import os
import json
import time
import logging
from typing import Optional
import requests
from sseclient import SSEClient
from dotenv import load_dotenv
from display import TFTDisplay, PicoScrollDisplay, QualiaESP32Display

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HUDClient:
    """Client for connecting to SSE endpoint and displaying HUD data"""
    
    def __init__(self):
        self.api_key = os.getenv('API_KEY')  # Optional - only used if provided
        
        self.signal_path = os.getenv(
            'SIGNAL_PATH', 
            'http://172.28.2.64:8000/api/v1/asset/signals/'
        )
        self.signal_name = os.getenv('SIGNAL_NAME', 'VDM_VehicleSpeed')
        
        # Construct full SSE URL
        self.sse_url = f"{self.signal_path.rstrip('/')}/{self.signal_name}"
        
        # Initialize display based on DISPLAY_TYPE environment variable
        display_type = os.getenv('DISPLAY_TYPE', 'tft').lower()
        
        if display_type == 'pico' or display_type == 'picoscroll':
            # Pico Scroll Pack via Raspberry Pi Pico
            logger.info("Initializing Pico Scroll display...")
            pico_port = os.getenv('PICO_SERIAL_PORT')  # Auto-detected if not set
            pico_baudrate = int(os.getenv('PICO_BAUDRATE', '115200'))
            self.display = PicoScrollDisplay(port=pico_port, baudrate=pico_baudrate)
            
        elif display_type in ['qualia', 'esp32', 'esp32-s3']:
            # Qualia ESP32-S3 RGB666 TFT Display
            logger.info("Initializing Qualia ESP32-S3 RGB666 TFT display...")
            esp32_port = os.getenv('ESP32_SERIAL_PORT')  # Auto-detected if not set
            esp32_baudrate = int(os.getenv('ESP32_BAUDRATE', '115200'))
            self.display = QualiaESP32Display(port=esp32_port, baudrate=esp32_baudrate)
            
        else:
            # Default: TFT35" Touch Shield
            logger.info("Initializing TFT35 display...")
            self.display = TFTDisplay()
        
        # Connection retry settings
        self.retry_delay = 5  # seconds
        self.max_retries = 10
        
    def get_headers(self) -> dict:
        """Get HTTP headers for SSE request"""
        headers = {
            'Accept': 'text/event-stream',
            'Cache-Control': 'no-cache'
        }
        # Only include x-api-key header if API_KEY is provided
        if self.api_key:
            headers['x-api-key'] = self.api_key
        return headers
    
    def parse_event_data(self, event_data: str) -> Optional[float]:
        """Parse event data and extract vehicle speed in MPH"""
        try:
            data = json.loads(event_data)
            # Try different possible key formats
            speed = data.get('VDM_VehicleSpeed') or data.get('value') or data.get('speed')
            if speed is not None:
                return float(speed)
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON: {e}")
        except (ValueError, TypeError) as e:
            logger.warning(f"Failed to convert speed to float: {e}")
        return None
    
    def connect_and_display(self):
        """Main loop: connect to SSE and update display"""
        retry_count = 0
        
        while retry_count < self.max_retries:
            try:
                logger.info(f"Connecting to SSE endpoint: {self.sse_url}")
                
                response = requests.get(
                    self.sse_url,
                    headers=self.get_headers(),
                    stream=True,
                    timeout=30
                )
                response.raise_for_status()
                
                # Reset retry count on successful connection
                retry_count = 0
                
                # Create SSE client
                client = SSEClient(response)
                
                logger.info("Connected to SSE stream, waiting for events...")
                
                # Process events
                for event in client.events():
                    if event.data:
                        speed = self.parse_event_data(event.data)
                        if speed is not None:
                            logger.info(f"Vehicle Speed: {speed} MPH")
                            self.display.update_speed(speed)
                    
                    # Handle keep-alive
                    if event.event == 'keep-alive':
                        continue
                
            except requests.exceptions.RequestException as e:
                retry_count += 1
                logger.error(f"Connection error (attempt {retry_count}/{self.max_retries}): {e}")
                if retry_count < self.max_retries:
                    logger.info(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    logger.error("Max retries reached. Exiting.")
                    raise
            
            except KeyboardInterrupt:
                logger.info("Received interrupt signal, shutting down...")
                break
            
            except Exception as e:
                logger.error(f"Unexpected error: {e}", exc_info=True)
                retry_count += 1
                if retry_count < self.max_retries:
                    time.sleep(self.retry_delay)
                else:
                    raise
        
        self.display.cleanup()


def main():
    """Entry point"""
    try:
        client = HUDClient()
        client.connect_and_display()
    except KeyboardInterrupt:
        logger.info("Application terminated by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise


if __name__ == '__main__':
    main()

