"""
Debug version of Pico Scroll script
Helps diagnose serial communication and display issues

Upload this to your Pico as main.py to see debug output
"""

import time
import sys
import uselect

print("=" * 40)
print("Pico Scroll Debug Script")
print("=" * 40)

# Try to import picoscroll
try:
    from picoscroll import PicoScroll
    print("✓ picoscroll library found")
    scroll = PicoScroll()
    scroll.clear()
    scroll.update()
    PICOSCROLL_AVAILABLE = True
except ImportError as e:
    print(f"✗ picoscroll not available: {e}")
    print("  You may need Pimoroni MicroPython firmware")
    scroll = None
    PICOSCROLL_AVAILABLE = False
except Exception as e:
    print(f"✗ Error initializing scroll: {e}")
    scroll = None
    PICOSCROLL_AVAILABLE = False

print("\nWaiting for serial data...")
print("Reading from sys.stdin...")

# Set up polling for stdin (works better than blocking read)
poller = uselect.poll()
poller.register(sys.stdin, uselect.POLLIN)

buffer = ""
line_count = 0

while True:
    try:
        # Check if data is available (non-blocking)
        if poller.poll(100):  # 100ms timeout
            # Read available data
            chunk = sys.stdin.read(1)
            if chunk:
                buffer += chunk
                # Check for newline
                if '\n' in buffer:
                    line = buffer.strip()
                    buffer = ""
                    
                    if line:
                        line_count += 1
                        print(f"[{line_count}] Received: '{line}'")
                        
                        # Try to parse as number
                        try:
                            speed = float(line)
                            print(f"  Parsed as speed: {speed} MPH")
                            
                            # Display on scroll if available
                            if PICOSCROLL_AVAILABLE and scroll:
                                try:
                                    # Clear and write speed
                                    scroll.clear()
                                    speed_str = f"{int(speed)}"
                                    
                                    # Try different display methods
                                    # Method 1: write_text (if available)
                                    try:
                                        scroll.write_text(speed_str, 0, 0)
                                    except AttributeError:
                                        # Method 2: text (alternative API)
                                        try:
                                            scroll.text(speed_str, 0, 0, 0, 7)  # x, y, color, brightness
                                        except AttributeError:
                                            # Method 3: set_pixel (manual)
                                            print(f"  Displaying manually (API may differ)")
                                            for i, char in enumerate(speed_str[:17]):  # Max 17 chars width
                                                # Simple numeric display - map digits to pixels
                                                pass
                                    
                                    scroll.update()
                                    print(f"  ✓ Display updated: {speed_str}")
                                except Exception as e:
                                    print(f"  ✗ Display error: {e}")
                            else:
                                print(f"  (No display available)")
                                
                        except ValueError:
                            print(f"  Not a number, ignoring")
                else:
                    # Buffer but no newline yet, continue reading
                    continue
        else:
            # No data available, small delay
            time.sleep(0.01)
            
    except KeyboardInterrupt:
        print("\n\nStopping...")
        if PICOSCROLL_AVAILABLE and scroll:
            scroll.clear()
            scroll.update()
        break
    except Exception as e:
        print(f"\nError: {e}")
        import sys
        sys.print_exception(e)
        time.sleep(0.1)


