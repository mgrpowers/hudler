# hudler
Giving your HUD-less vehicle a HUD

## Overview

Real-time vehicle speed display (MPH) on a TFT35" touch shield connected to a Raspberry Pi. Connects to a Server-Sent Events (SSE) endpoint and displays vehicle speed data in real-time.

## Hardware Requirements

**Option 1: TFT35" Display**
- Raspberry Pi (3B+ or newer recommended)
- TFT35" Touch Shield for Raspberry Pi
- Power supply for Raspberry Pi
- Network connection

**Option 2: Pico Scroll Display**
- Raspberry Pi (3B+ or newer recommended) OR any computer with Python
- Raspberry Pi Pico with Pimoroni Pico Scroll Pack attached
- USB cable to connect Pico to Raspberry Pi/computer
- Network connection (for Raspberry Pi)

**Option 3: Qualia ESP32-S3 RGB666 TFT Display**
- Raspberry Pi (3B+ or newer recommended) OR any computer with Python
- Qualia ESP32-S3 RGB666 40p TFT Display
- USB cable to connect ESP32-S3 to Raspberry Pi/computer
- Network connection (for Raspberry Pi)

## Installation

### 1. Set Up Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Note:** Always activate the virtual environment before running scripts:
```bash
source venv/bin/activate
```

### 1b. Alternative: Install System-Wide (Not Recommended)

If you prefer not to use a virtual environment:

```bash
# Install Python dependencies
pip install -r requirements.txt

# On Raspberry Pi, also install GPIO and SPI libraries:
pip install RPi.GPIO spidev
```

### 2. Configure Environment Variables

Copy the example environment file and set your values:

```bash
cp .env.example .env
```

Edit `.env` and set:
- `API_KEY`: (Optional) API authentication key - only needed if your endpoint requires authentication
- `SIGNAL_PATH`: Base path for SSE endpoint (default: `http://172.28.1.64:8000/api/v1/asset/signals/`)
- `SIGNAL_NAME`: Signal name to subscribe to (default: `VDM_VehicleSpeed`)
- `DISPLAY_TYPE`: Display type - `tft` (default) or `pico`
- `PICO_SERIAL_PORT`: Serial port for Pico (auto-detected if not set)
- `PICO_BAUDRATE`: Serial baudrate for Pico (default: `115200`)

### 3. Load Environment Variables

You can either:
- Export variables in your shell before running:
  ```bash
  export API_KEY=your_key_here
  export SIGNAL_PATH=http://172.28.1.64:8000/api/v1/asset/signals/
  export SIGNAL_NAME=VDM_VehicleSpeed
  ```

- Use a `.env` file with `python-dotenv` (add to requirements.txt and use):
  ```python
  from dotenv import load_dotenv
  load_dotenv()
  ```

### 4. Display Configuration

#### TFT35" Display (Default)

The application will automatically detect the display method:

- **Framebuffer mode**: If `/dev/fb1` exists, uses framebuffer rendering
- **PIL mode**: Falls back to PIL-based rendering if framebuffer not available
- **Simulation mode**: Runs without display output (for testing)

To specify a custom framebuffer device:
```bash
export FRAMEBUFFER=/dev/fb1
```

#### Pico Scroll Display

To use a Pimoroni Pico Scroll Pack connected to a Raspberry Pi Pico:

1. **Set display type:**
   ```bash
   export DISPLAY_TYPE=pico
   ```

2. **Optional: Specify Pico serial port** (auto-detected if not set):
   ```bash
   export PICO_SERIAL_PORT=/dev/ttyACM0  # or /dev/tty.usbmodemXXX on macOS
   ```

3. **Test serial connection first:**
   ```bash
   python test_pico_serial.py
   ```
   This will send test speed values to your Pico to verify communication.

4. **Pico firmware requirements:**
   - Flash Pimoroni MicroPython firmware to your Pico
   - Upload a MicroPython script to the Pico that reads from serial and displays on Scroll Pack
   - See `simpletest.py` for example Pico code

#### Qualia ESP32-S3 RGB666 TFT Display

To use a Qualia ESP32-S3 RGB666 40p TFT Display:

1. **Set display type:**
   ```bash
   export DISPLAY_TYPE=qualia
   # or
   export DISPLAY_TYPE=esp32
   ```

2. **Optional: Specify ESP32 serial port** (auto-detected if not set):
   ```bash
   export ESP32_SERIAL_PORT=/dev/ttyUSB0  # or /dev/ttyACM0, /dev/tty.usbserial-XXX on macOS
   ```

3. **Test serial connection first:**
   ```bash
   python test_esp32_serial.py
   ```
   This will send test speed values to your ESP32-S3 to verify communication.

4. **ESP32-S3 firmware requirements:**
   - Flash MicroPython or Arduino firmware to your ESP32-S3
   - Upload code that reads from serial and displays on RGB666 TFT
   - See `esp32_qualia_example.py` for example ESP32-S3 code

## Usage

**Important:** Make sure your virtual environment is activated before running scripts:

```bash
source venv/bin/activate
```

### Testing Serial Connections

Before running the full application, test serial communication:

**For Pico Scroll:**
```bash
python test_pico_serial.py
```

**For ESP32-S3:**
```bash
python test_esp32_serial.py
```

These scripts will:
- Auto-detect the device's serial port
- Send test speed values (0, 25, 50, 65, 75, 85 MPH)
- Simulate rapid real-time updates (50ms intervals)
- Verify near real-time communication is working

You can also specify the port manually:
```bash
python test_esp32_serial.py /dev/ttyUSB0
python test_esp32_serial.py /dev/ttyUSB0 115200  # with custom baudrate
```

### Running the Main Application

Run the application:

```bash
python main.py
```

The application will:
1. Connect to the SSE endpoint using the configured API key
2. Listen for `VDM_VehicleSpeed` events
3. Display the speed value on the configured display (TFT35" or Pico Scroll)
4. Automatically reconnect on connection errors

**Testing Pico Serial Connection:**

See the "Testing Pico Serial Connection (Mac to Pico)" section below for instructions.

## Signal Format

The application expects SSE events with JSON data containing the vehicle speed. The signal value can be provided in any of these formats:

```json
{"VDM_VehicleSpeed": 65.5}
{"value": 65.5}
{"speed": 65.5}
```

## Troubleshooting

### Display Not Showing
- Verify framebuffer device exists: `ls -l /dev/fb*`
- Check display is properly connected to Raspberry Pi
- Try running with `sudo` if permission issues occur

### Connection Errors
- Verify network connectivity to the SSE endpoint
- Check API key is correct and has proper permissions
- Verify the signal path and signal name are correct
- Check firewall settings if connecting over network

### No Speed Data
- Verify the signal name matches what's being sent from the server
- Check server logs for connection and event delivery
- Enable debug logging by modifying log level in `main.py`

## Development

The application consists of:
- `main.py`: SSE client and main application loop
- `display.py`: TFT35" display interface and rendering
- `requirements.txt`: Python package dependencies
