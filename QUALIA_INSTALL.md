# Installing Qualia Library on ESP32-S3

The Qualia library needs to be installed on your ESP32-S3 before the display will work.

## Installation Methods

### Method 1: CircuitPython (Recommended)

1. **Download the library bundle:**
   - Go to: https://circuitpython.org/libraries
   - Download the bundle matching your CircuitPython version
   - Extract the zip file

2. **Find the library:**
   - Look in the extracted folder for `lib/adafruit_qualia/`
   - **IMPORTANT:** Make sure the folder contains `.py` or `.mpy` files, not just metadata

3. **Copy to ESP32-S3:**
   - Connect ESP32-S3 via USB (mounts as `CIRCUITPY` drive)
   - Copy the entire `adafruit_qualia` folder to `CIRCUITPY/lib/`
   - The structure should be: `CIRCUITPY/lib/adafruit_qualia/`
   - **Make sure you copy the actual Python files, not just the folder!**

4. **Verify installation:**
   - The folder should contain files like `__init__.py` or `__init__.mpy`
   - Run the diagnostic: Upload `qualia_diagnose.py` to check
   - Or test: `from adafruit_qualia import Qualia`

### Method 2: MicroPython (mpremote)

```bash
# Install using mpremote
mpremote mip install github:fivesixzero/qualia

# Or install from local file
mpremote cp qualia /lib/
```

### Method 3: Thonny IDE

1. Open Thonny
2. Connect to your ESP32-S3
3. Go to Tools → Manage packages
4. Search for "qualia" or install from GitHub URL
5. Or manually copy the `qualia` folder to the device

### Method 4: Manual Copy (CircuitPython)

1. Download the qualia library from GitHub
2. Connect ESP32-S3 (mounts as CIRCUITPY)
3. Create `lib` folder if it doesn't exist: `CIRCUITPY/lib/`
4. Copy the entire `qualia` folder into `CIRCUITPY/lib/`
5. Eject and reconnect the device

## Verify Installation

Run this in the ESP32-S3 REPL:

```python
import qualia
from qualia import Qualia
display = Qualia()
print("Qualia library loaded successfully!")
```

## Alternative: Direct Hardware Access

If the Qualia library isn't available, you might need to use the underlying display drivers directly. The Qualia ESP32-S3 RGB666 typically uses:

- `displayio` (CircuitPython)
- `framebuf` (MicroPython)
- Direct RGB666 parallel interface

Check the Qualia documentation for the exact hardware interface and driver requirements.

## Troubleshooting

**"ModuleNotFoundError: No module named 'qualia'"**
- Library not installed or in wrong location
- Make sure it's in `lib/qualia/` (CircuitPython) or `/lib/qualia/` (MicroPython)

**"ImportError: cannot import name 'Qualia'"**
- Library installed but wrong version or incomplete
- Re-download and reinstall the library

**Library installed but still not working**
- Check ESP32-S3 has enough free space
- Verify the library is compatible with your firmware version
- Check if you need additional dependencies

