"""
MicroPython/Arduino example for Qualia ESP32-S3 RGB666 40p TFT Display
Receives speed values over USB serial and displays on the RGB666 TFT

To use:
1. Flash MicroPython or Arduino firmware to your ESP32-S3
2. Upload this code to your ESP32-S3
3. Connect ESP32-S3 to Raspberry Pi/computer via USB
4. Run the host application which will send speed values

IMPORTANT: This must be saved as main.py (MicroPython) or uploaded as sketch (Arduino)
"""

# MicroPython version
import time
import sys
import uselect

# Try to import Qualia display library
# Your display: 3.2" 320x820 bar display (TL032FWV01CT-I1440A)
QUALIA_AVAILABLE = False
display = None

# Try Option 1: Direct import from displays folder (bypass submodule)
try:
    import sys
    sys.path.insert(0, '/lib/adafruit_qualia/displays')
    import bar320x820
    
    # Try to instantiate - check what's available
    if hasattr(bar320x820, 'Bar320x820'):
        display = bar320x820.Bar320x820()
        QUALIA_AVAILABLE = True
        print("✓ Qualia library loaded: Bar320x820()")
    elif hasattr(bar320x820, 'Qualia'):
        display = bar320x820.Qualia()
        QUALIA_AVAILABLE = True
        print("✓ Qualia library loaded: bar320x820.Qualia()")
    else:
        # Try calling the module itself
        try:
            display = bar320x820()
            QUALIA_AVAILABLE = True
            print("✓ Qualia library loaded: bar320x820()")
        except:
            print(f"  bar320x820 contents: {dir(bar320x820)[:10]}")
except (ImportError, AttributeError, TypeError) as e:
    print(f"  Direct bar320x820 import failed: {e}")

# Try Option 2: Qualia factory (without board.DISPLAY - it might not exist)
if not QUALIA_AVAILABLE:
    try:
        from adafruit_qualia import Qualia
        # Try without board.DISPLAY first
        try:
            display = Qualia("bar320x820")
            QUALIA_AVAILABLE = True
            print("✓ Qualia library loaded: Qualia('bar320x820')")
        except (TypeError, ValueError) as e:
            print(f"  Qualia('bar320x820') failed: {e}")
            # Try with board if available
            try:
                import board
                if hasattr(board, 'DISPLAY'):
                    display = Qualia(board.DISPLAY, "bar320x820")
                    QUALIA_AVAILABLE = True
                    print("✓ Qualia library loaded: Qualia(board.DISPLAY, 'bar320x820')")
                else:
                    print("  board.DISPLAY not available")
            except ImportError:
                print("  board module not available")
    except (ImportError, AttributeError, TypeError) as e:
        print(f"  Qualia factory failed: {e}")

if not QUALIA_AVAILABLE:
    print("✗ Qualia library not available")
    print("  Install adafruit_qualia library for ESP32-S3")
    print("  Make sure it's in /lib/adafruit_qualia/")

# Alternative: If using Arduino/PlatformIO, adapt this to C++


def display_speed(display_obj, speed_value):
    """Display speed on Qualia RGB666 TFT"""
    if not QUALIA_AVAILABLE or display_obj is None:
        print(f"Speed: {speed_value} MPH")
        return
    
    # Display is already initialized when created - no init() needed
    
    try:
        # Format speed as text
        speed_text = f"{int(speed_value)}"
        mph_text = "MPH"
        
        # Use displayio for rendering (Qualia uses displayio, not direct fill/text)
        import displayio
        from adafruit_display_text import label
        import terminalio
        
        # Get the actual display object
        actual_display = display_obj
        if hasattr(display_obj, 'display'):
            actual_display = display_obj.display
        elif hasattr(display_obj, '_display'):
            actual_display = display_obj._display
        else:
            # Try board.DISPLAY
            try:
                import board
                actual_display = board.DISPLAY
            except:
                actual_display = display_obj
        
        # Get display dimensions
        width = actual_display.width if hasattr(actual_display, 'width') else 320
        height = actual_display.height if hasattr(actual_display, 'height') else 820
        
        # Create a new group for this frame
        group = displayio.Group()
        
        # Create black background
        bitmap = displayio.Bitmap(width, height, 1)
        palette = displayio.Palette(1)
        palette[0] = 0x000000  # Black
        bg_tile = displayio.TileGrid(bitmap, pixel_shader=palette)
        group.append(bg_tile)
        
        # Create speed text (large, centered)
        # Center horizontally: width/2, vertically: height/2 - 20
        speed_label = label.Label(
            terminalio.FONT, 
            text=speed_text, 
            color=0xFFFFFF, 
            x=width//2, 
            y=height//2 - 20,
            anchor_point=(0.5, 0.5),
            anchored_position=(width//2, height//2 - 20),
            scale=4
        )
        group.append(speed_label)
        
        # Create MPH text (smaller, below speed)
        mph_label = label.Label(
            terminalio.FONT, 
            text=mph_text, 
            color=0x888888, 
            x=width//2, 
            y=height//2 + 40,
            anchor_point=(0.5, 0.5),
            anchored_position=(width//2, height//2 + 40),
            scale=2
        )
        group.append(mph_label)
        
        # Set root group on the display
        if hasattr(actual_display, 'root_group'):
            actual_display.root_group = group
        elif hasattr(display_obj, 'root_group'):
            display_obj.root_group = group
        else:
            try:
                import board
                board.DISPLAY.root_group = group
            except:
                pass
        
    except OSError as e:
        if e.errno == 30:  # Read-only filesystem
            print(f"Display error: Read-only filesystem (errno 30)")
            print("  Display operations may be limited. Check filesystem configuration.")
        else:
            print(f"Display error: {e}")
    except Exception as e:
        print(f"Display error: {e}")


def main():
    """Main loop: read from serial and display speed"""
    
    # Use the global display object
    global display
    if QUALIA_AVAILABLE and display:
        try:
            # Try to remount filesystem as read-write if possible
            try:
                import os
                # Check if we can remount (some ESP32 builds support this)
                try:
                    os.mount('/', '/', readonly=False)
                    print("✓ Filesystem remounted as read-write")
                except (OSError, AttributeError):
                    # Filesystem remount not supported or already read-write
                    pass
            except ImportError:
                pass
            
            # Display is already initialized when created
            display.fill(0)  # Clear to black
            display.show()
            print("✓ Qualia RGB666 TFT initialized")
            
            # Display "IDLE" message to verify display is working
            # Your display: 320x820, center at (160, 410)
            try:
                # Try text() method - might need different approach
                try:
                    display.text("IDLE", 160, 410, 0xFFFFFF, size=6)
                    display.show()
                    print("✓ 'IDLE' message displayed - if you see this on the display, hardware is working!")
                except AttributeError:
                    # Maybe need to use displayio for text
                    import displayio
                    from adafruit_display_text import label
                    import terminalio
                    
                    # Create text label
                    text_area = label.Label(terminalio.FONT, text="IDLE", color=0xFFFFFF, x=160, y=410)
                    if not hasattr(display, 'root_group') or display.root_group is None:
                        display.root_group = displayio.Group()
                    display.root_group.append(text_area)
                    print("✓ 'IDLE' message displayed using displayio - if you see this on the display, hardware is working!")
            except OSError as e:
                if e.errno == 30:  # Read-only filesystem
                    print("⚠ Read-only filesystem warning, but display may still work")
                    print("  Try re-flashing ESP32 filesystem or using RAM-only operations")
                else:
                    raise
            except Exception as e:
                print(f"  Display text error: {e}")
                print("  Display initialized but text rendering may need adjustment")
            
        except OSError as e:
            if e.errno == 30:  # Read-only filesystem error
                print(f"✗ Read-only filesystem error (errno 30)")
                print("  The Qualia library may be trying to write files.")
                print("  Solutions:")
                print("  1. Re-flash ESP32 filesystem")
                print("  2. Use a build that doesn't require file writes")
                print("  3. Check if Qualia library has a RAM-only mode")
            else:
                print(f"✗ Failed to initialize Qualia display: {e}")
            import sys
            try:
                sys.print_exception(e)
            except:
                pass
            display = None
        except Exception as e:
            print(f"✗ Failed to initialize Qualia display: {e}")
            import sys
            try:
                sys.print_exception(e)
            except:
                pass
            display = None
    else:
        print("Running without Qualia display (simulation mode)")
    
    print("\nWaiting for speed data...")
    print("Format: one number per line (e.g., '65\\n' for 65 MPH)")
    print("When data arrives, 'IDLE' will be replaced with speed values.\n")
    
    # Use polling for better non-blocking reads
    poller = uselect.poll()
    poller.register(sys.stdin, uselect.POLLIN)
    
    buffer = ""
    line_count = 0
    
    while True:
        try:
            # Poll for incoming data (non-blocking, 100ms timeout)
            if poller.poll(100):
                # Read character by character
                char = sys.stdin.read(1)
                if char:
                    buffer += char
                    # Check for newline
                    if '\n' in buffer:
                        # Process complete line
                        line = buffer.strip()
                        buffer = ""
                        
                        if line:
                            line_count += 1
                            print(f"[{line_count}] Received: '{line}'")
                            
                            try:
                                speed = float(line)
                                print(f"  → Displaying: {speed} MPH")
                                display_speed(display, speed)
                            except ValueError:
                                print(f"  → Not a number, ignoring")
            else:
                # No data available, small delay
                time.sleep(0.01)
                
        except KeyboardInterrupt:
            print("\n\nStopping...")
            if display:
                try:
                    display.fill(0)
                    display.show()
                except:
                    pass
            break
        except Exception as e:
            print(f"Error: {e}")
            import sys
            try:
                sys.print_exception(e)
            except:
                pass
            time.sleep(0.1)


if __name__ == "__main__":
    main()

