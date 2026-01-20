"""
Bare minimum test for Qualia ESP32-S3 RGB666 TFT Display
Upload this as main.py to test if the display hardware is working
"""

import time

# Try to import Qualia display library - try different names
QUALIA_AVAILABLE = False
Qualia = None

# Try Option 1: adafruit_qualia.displays (most likely - Qualia is in displays submodule)
try:
    from adafruit_qualia.displays import Qualia
    QUALIA_AVAILABLE = True
    print("✓ Qualia library loaded: from adafruit_qualia.displays")
except ImportError:
    pass

# Try Option 1b: adafruit_qualia directly
if not QUALIA_AVAILABLE:
    try:
        from adafruit_qualia import Qualia
        QUALIA_AVAILABLE = True
        print("✓ Qualia library loaded: from adafruit_qualia")
    except ImportError:
        pass

# Try Option 2: qualia
if not QUALIA_AVAILABLE:
    try:
        from qualia import Qualia
        QUALIA_AVAILABLE = True
        print("✓ Qualia library loaded: from qualia")
    except ImportError:
        pass

# Try Option 3: qualia_esp32s3
if not QUALIA_AVAILABLE:
    try:
        from qualia_esp32s3 import Qualia
        QUALIA_AVAILABLE = True
        print("✓ Qualia library loaded: from qualia_esp32s3")
    except ImportError:
        pass

if not QUALIA_AVAILABLE:
    print("✗ Qualia library not available")
    print("\nTo install:")
    print("1. Go to: https://circuitpython.org/libraries")
    print("2. Download bundle matching your CircuitPython version")
    print("3. Extract and copy 'adafruit_qualia' folder to CIRCUITPY/lib/")
    print("4. Restart ESP32-S3")

def main():
    """Minimal test - just show something on screen"""
    
    if not QUALIA_AVAILABLE:
        print("Cannot test - Qualia library not available")
        return
    
    try:
        print("Initializing Qualia display...")
        display = Qualia()
        display.init()
        
        print("Clearing display...")
        display.fill(0)  # Fill with black
        display.show()
        time.sleep(0.5)
        
        print("Drawing test pattern...")
        # Draw a simple test pattern
        # Fill screen with red
        display.fill(0xFF0000)  # Red
        display.show()
        time.sleep(1)
        
        # Fill screen with green
        display.fill(0x00FF00)  # Green
        display.show()
        time.sleep(1)
        
        # Fill screen with blue
        display.fill(0x0000FF)  # Blue
        display.show()
        time.sleep(1)
        
        # Fill screen with white
        display.fill(0xFFFFFF)  # White
        display.show()
        time.sleep(1)
        
        # Clear to black
        display.fill(0)  # Black
        display.show()
        
        print("Displaying text...")
        # Try to display text
        try:
            display.text("TEST", 400, 240, 0xFFFFFF, size=8)  # White text, centered
            display.show()
            print("✓ Text displayed - you should see 'TEST' on screen")
        except Exception as e:
            print(f"Text display failed: {e}")
            print("  But color test worked, so display hardware is functional")
        
        print("\n✓ Display test complete!")
        print("If you saw colors change and/or text, the display is working.")
        print("Press Ctrl+C to exit.")
        
        # Keep running so you can see the display
        while True:
            time.sleep(1)
            
    except OSError as e:
        if e.errno == 30:
            print("✗ Read-only filesystem error")
            print("  The display may still work, but library can't write files")
            print("  Try creating boot.py with: import storage; storage.remount('/', False)")
        else:
            print(f"✗ Error: {e}")
    except Exception as e:
        print(f"✗ Failed to initialize display: {e}")
        import sys
        try:
            sys.print_exception(e)
        except:
            pass

if __name__ == "__main__":
    main()

