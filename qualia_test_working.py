"""
Working test for Qualia ESP32-S3 RGB666 40p
Since Qualia is available directly, let's use it properly
"""

import time
import board

# Qualia is available directly from adafruit_qualia
from adafruit_qualia import Qualia

print("Initializing Qualia display...")

# Try different initialization patterns
display = None

# Pattern 1: Qualia(board.DISPLAY) - auto-detect
try:
    display = Qualia(board.DISPLAY)
    print("✓ Qualia(board.DISPLAY) - auto-detect")
except Exception as e:
    print(f"  Auto-detect failed: {e}")

# Pattern 2: Qualia(board.DISPLAY, "round40")
if display is None:
    try:
        display = Qualia(board.DISPLAY, "round40")
        print("✓ Qualia(board.DISPLAY, 'round40')")
    except Exception as e:
        print(f"  round40 failed: {e}")

# Pattern 3: Qualia(board.DISPLAY, "square40")
if display is None:
    try:
        display = Qualia(board.DISPLAY, "square40")
        print("✓ Qualia(board.DISPLAY, 'square40')")
    except Exception as e:
        print(f"  square40 failed: {e}")

# Pattern 4: Check what Qualia actually needs
if display is None:
    print("\nChecking Qualia constructor requirements...")
    try:
        import inspect
        sig = inspect.signature(Qualia)
        print(f"  Qualia signature: {sig}")
    except:
        print("  Cannot inspect signature")
        # Try to see what happens with different argument counts
        print("  Trying different argument patterns...")
        for args in [
            (),
            (board.DISPLAY,),
            (board.DISPLAY, "round40"),
            (board.DISPLAY, "square40"),
            ("round40",),
            ("square40",),
        ]:
            try:
                display = Qualia(*args)
                print(f"  ✓ Qualia{args} worked!")
                break
            except Exception as e:
                print(f"  ✗ Qualia{args} failed: {type(e).__name__}")

if display:
    print("\n✓ Display initialized!")
    try:
        # Initialize display
        try:
            display.init()
        except AttributeError:
            pass  # init() might not be needed
        
        # Show colors
        colors = [
            (0xFF0000, "RED"),
            (0x00FF00, "GREEN"),
            (0x0000FF, "BLUE"),
            (0xFFFFFF, "WHITE"),
            (0x000000, "BLACK")
        ]
        
        print("Cycling through colors...")
        while True:
            for color, name in colors:
                print(f"  Showing {name}...")
                try:
                    display.fill(color)
                    display.show()
                except AttributeError:
                    # Maybe it uses different methods
                    try:
                        display.root_group = displayio.Group()
                        # Create bitmap and fill
                        import displayio
                        bitmap = displayio.Bitmap(display.width, display.height, 1)
                        palette = displayio.Palette(1)
                        palette[0] = color
                        tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)
                        display.root_group.append(tile_grid)
                    except Exception as e2:
                        print(f"    Display error: {e2}")
                time.sleep(2)
    except Exception as e:
        print(f"Display error: {e}")
        import sys
        try:
            sys.print_exception(e)
        except:
            pass
else:
    print("\n✗ Could not initialize display")
    print("Check the error messages above to see what Qualia() needs")

