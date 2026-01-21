"""
Qualia ESP32-S3 with Wi-Fi - Direct SSE Connection
Connects directly to SSE endpoint and displays speed on Qualia display
No Raspberry Pi needed!

To use:
1. Create settings.toml on CIRCUITPY drive with:
   CIRCUITPY_WIFI_SSID = "your_wifi_name"
   CIRCUITPY_WIFI_PASSWORD = "your_wifi_password"
   
2. Set environment variables (or hardcode):
   - SIGNAL_PATH: http://172.28.1.64:8000/api/v1/asset/signals/
   - SIGNAL_NAME: VDM_VehicleSpeed
   - API_KEY: (optional) your API key

3. Upload this as main.py to ESP32-S3
"""

import time
import os
import wifi
import socketpool
import ssl
import adafruit_requests
from adafruit_qualia import Qualia
import displayio
from adafruit_display_text import label
import terminalio

# Configuration
SIGNAL_PATH = os.getenv('SIGNAL_PATH', 'http://172.28.1.64:8000/api/v1/asset/signals/')
SIGNAL_NAME = os.getenv('SIGNAL_NAME', 'VDM_VehicleSpeed')
API_KEY = os.getenv('API_KEY')  # Optional

SSE_URL = f"{SIGNAL_PATH.rstrip('/')}/{SIGNAL_NAME}"

# Initialize Qualia display
print("Initializing Qualia display...")
display = Qualia('bar320x820')
print("✓ Display initialized")

# Get actual display object
actual_display = display
if hasattr(display, 'display'):
    actual_display = display.display
elif hasattr(display, '_display'):
    actual_display = display._display
else:
    try:
        import board
        actual_display = board.DISPLAY
    except:
        actual_display = display

width = actual_display.width if hasattr(actual_display, 'width') else 320
height = actual_display.height if hasattr(actual_display, 'height') else 820
print(f"Display size: {width}x{height}")

# Create display group for speed
speed_group = displayio.Group()

# Black background
bg_bitmap = displayio.Bitmap(width, height, 1)
bg_palette = displayio.Palette(1)
bg_palette[0] = 0x000000
bg_tile = displayio.TileGrid(bg_bitmap, pixel_shader=bg_palette)
speed_group.append(bg_tile)

# Speed text label (will be updated)
speed_label = label.Label(
    terminalio.FONT,
    text="IDLE",
    color=0xFFFFFF,
    x=width//2,
    y=height//2 - 20,
    anchor_point=(0.5, 0.5),
    anchored_position=(width//2, height//2 - 20),
    scale=4
)
speed_group.append(speed_label)

# MPH label
mph_label = label.Label(
    terminalio.FONT,
    text="MPH",
    color=0x888888,
    x=width//2,
    y=height//2 + 40,
    anchor_point=(0.5, 0.5),
    anchored_position=(width//2, height//2 + 40),
    scale=2
)
speed_group.append(mph_label)

# Set root group
if hasattr(actual_display, 'root_group'):
    actual_display.root_group = speed_group
elif hasattr(display, 'root_group'):
    display.root_group = speed_group
else:
    try:
        import board
        board.DISPLAY.root_group = speed_group
    except:
        pass

print("✓ Display ready")

# Connect to Wi-Fi
print("\nConnecting to Wi-Fi...")
try:
    wifi.radio.connect(
        os.getenv('CIRCUITPY_WIFI_SSID'),
        os.getenv('CIRCUITPY_WIFI_PASSWORD')
    )
    print(f"✓ Connected to Wi-Fi: {wifi.radio.ipv4_address}")
except Exception as e:
    print(f"✗ Wi-Fi connection failed: {e}")
    speed_label.text = "NO WIFI"
    raise

# Create socket pool and requests session
pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool, ssl.create_default_context())

# Prepare headers
headers = {
    'Accept': 'text/event-stream',
    'Cache-Control': 'no-cache',
}
if API_KEY:
    headers['x-api-key'] = API_KEY

print(f"\nConnecting to SSE endpoint: {SSE_URL}")
print("Waiting for speed data...\n")

# Main loop: connect to SSE and update display
retry_count = 0
max_retries = 10
retry_delay = 5

while retry_count < max_retries:
    try:
        # Connect to SSE endpoint
        response = requests.get(SSE_URL, headers=headers, stream=True)
        response.raise_for_status()
        
        print("✓ Connected to SSE stream")
        retry_count = 0  # Reset on successful connection
        
        # Process SSE stream
        buffer = ""
        while True:
            # Read data in chunks
            chunk = response.raw.read(1024)
            if not chunk:
                break
            
            buffer += chunk.decode('utf-8', errors='ignore')
            
            # Process complete lines
            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                line = line.strip()
                
                if line.startswith('data: '):
                    # Parse JSON data
                    data_str = line[6:]  # Remove 'data: ' prefix
                    try:
                        import json
                        data = json.loads(data_str)
                        
                        # Extract speed value
                        speed = data.get('VDM_VehicleSpeed') or data.get('value') or data.get('speed')
                        if speed is not None:
                            speed_value = float(speed)
                            speed_text = f"{int(speed_value)}"
                            
                            # Update display
                            speed_label.text = speed_text
                            print(f"Speed: {speed_text} MPH")
                    except (json.JSONDecodeError, ValueError, TypeError) as e:
                        print(f"Parse error: {e}")
                        continue
                
                elif line == '':
                    # Empty line (heartbeat)
                    continue
                elif line.startswith('event: '):
                    # Event type
                    event_type = line[7:]
                    if event_type == 'keep-alive':
                        continue
            
            time.sleep(0.1)  # Small delay to prevent tight loop
        
    except Exception as e:
        print(f"✗ Connection error: {e}")
        retry_count += 1
        if retry_count < max_retries:
            print(f"Retrying in {retry_delay} seconds... ({retry_count}/{max_retries})")
            speed_label.text = f"RETRY {retry_count}"
            time.sleep(retry_delay)
        else:
            speed_label.text = "ERROR"
            print("Max retries reached")
            raise

print("Exiting...")

