"""
Bare minimum test for Qualia ESP32-S3 RGB666 40p
Upload as main.py - just tries to import and show colors
"""

import time

# Try importing the base module first
try:
    import adafruit_qualia
    print("✓ adafruit_qualia module imported")
    print(f"  Available: {dir(adafruit_qualia)[:10]}")
except ImportError as e:
    print(f"✗ Cannot import adafruit_qualia: {e}")
    import sys
    try:
        sys.print_exception(e)
    except:
        pass

# Try different display imports
display = None

# Your display: 3.2" 320x820 bar display (TL032FWV01CT-I1440A)
# Try bar320x820 first!
try:
    from adafruit_qualia import Qualia
    import board
    # Try bar320x820 (your display)
    try:
        display = Qualia(board.DISPLAY, "bar320x820")
        print("✓ Loaded: Qualia(board.DISPLAY, 'bar320x820')")
    except (TypeError, ValueError) as e:
        print(f"  bar320x820 failed: {e}")
        # Try other display types as fallback
        try:
            display = Qualia(board.DISPLAY, "round40")
            print("✓ Loaded: Qualia(board.DISPLAY, 'round40')")
        except (TypeError, ValueError):
            try:
                display = Qualia(board.DISPLAY, "square40")
                print("✓ Loaded: Qualia(board.DISPLAY, 'square40')")
            except (TypeError, ValueError):
                try:
                    display = Qualia(board.DISPLAY)
                    print("✓ Loaded: Qualia(board.DISPLAY)")
                except (TypeError, ValueError) as e2:
                    print(f"  All Qualia patterns failed: {e2}")
except (ImportError, AttributeError) as e:
    print(f"  Qualia import failed: {e}")

if display:
    try:
        # Initialize and show colors
        display.init()
        print("Display initialized!")
        
        colors = [0xFF0000, 0x00FF00, 0x0000FF, 0xFFFFFF, 0x000000]
        names = ["RED", "GREEN", "BLUE", "WHITE", "BLACK"]
        
        while True:
            for color, name in zip(colors, names):
                print(f"Showing {name}...")
                display.fill(color)
                display.show()
                time.sleep(2)
    except Exception as e:
        print(f"Display error: {e}")
        import sys
        try:
            sys.print_exception(e)
        except:
            pass
else:
    print("\n✗ Could not load display")
    print("Check the serial console for import errors")

