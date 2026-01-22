"""
CircuitPython code for Qualia ESP32-S3 RGB666 40p TFT Display
Receives speed values over USB serial and displays on the RGB666 TFT

To use:
1. Flash CircuitPython firmware to your ESP32-S3
2. Copy this file as code.py to your ESP32-S3 CIRCUITPY drive
   (CircuitPython automatically runs code.py on boot)
3. Connect ESP32-S3 to Raspberry Pi/computer via USB
4. Run the host application which will send speed values

IMPORTANT: This file must be named code.py on the CIRCUITPY drive
CircuitPython automatically executes code.py when the device boots.
"""

# CircuitPython version
import time
import sys
import supervisor

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


# Cache display objects to avoid recreating them (optimization for high message rates)
_display_cache = {
    'actual_display': None,
    'width': None,
    'height': None,
    'speed_label': None,
    'mph_label': None,
    'group': None
}

def _get_display_info(display_obj):
    """Get and cache display info (only do this once)"""
    if _display_cache['actual_display'] is None:
        if hasattr(display_obj, 'display'):
            _display_cache['actual_display'] = display_obj.display
        elif hasattr(display_obj, '_display'):
            _display_cache['actual_display'] = display_obj._display
        else:
            try:
                import board
                _display_cache['actual_display'] = board.DISPLAY
            except:
                _display_cache['actual_display'] = display_obj
        
        # Get physical dimensions BEFORE rotation
        phys_width = _display_cache['actual_display'].width if hasattr(_display_cache['actual_display'], 'width') else 320
        phys_height = _display_cache['actual_display'].height if hasattr(_display_cache['actual_display'], 'height') else 820
        print(f"  Physical dimensions before rotation: {phys_width}x{phys_height}")
        
        # Store physical dimensions for bitmap (bitmap always uses physical size)
        _display_cache['phys_width'] = phys_width
        _display_cache['phys_height'] = phys_height
        
        # Set display rotation to 90 degrees + flip for HUD
        # HUD needs: rotated 90° + horizontally flipped (mirrored) + vertically flipped (upside down)
        # This makes it readable when reflected in windshield
        try:
            if hasattr(_display_cache['actual_display'], 'rotation'):
                # Rotation: 90 degrees (portrait mode)
                _display_cache['actual_display'].rotation = 90
                print(f"  Set rotation to 90 degrees")
            
            # Try to set horizontal flip (mirror left-right) - some displays support this
            if hasattr(_display_cache['actual_display'], 'horizontal_flip'):
                _display_cache['actual_display'].horizontal_flip = True
                print(f"  Enabled horizontal flip (mirror)")
            elif hasattr(_display_cache['actual_display'], 'flip_x'):
                _display_cache['actual_display'].flip_x = True
                print(f"  Enabled flip_x (mirror)")
            elif hasattr(_display_cache['actual_display'], 'mirror_x'):
                _display_cache['actual_display'].mirror_x = True
                print(f"  Enabled mirror_x")
            
            # Try to set vertical flip (upside down) - needed for windshield reflection
            if hasattr(_display_cache['actual_display'], 'vertical_flip'):
                _display_cache['actual_display'].vertical_flip = True
                print(f"  Enabled vertical flip (upside down)")
            elif hasattr(_display_cache['actual_display'], 'flip_y'):
                _display_cache['actual_display'].flip_y = True
                print(f"  Enabled flip_y (upside down)")
            elif hasattr(_display_cache['actual_display'], 'mirror_y'):
                _display_cache['actual_display'].mirror_y = True
                print(f"  Enabled mirror_y (upside down)")
        except Exception as e:
            print(f"  Could not set rotation/flip: {e}")
        
        # Store flip state for later use in label positioning
        _display_cache['needs_flip'] = True
        
        # Get dimensions AFTER rotation for coordinates
        # After 90° rotation, CircuitPython may swap width/height
        # For coordinates: after rotation, x can go up to 820, y up to 320
        # Store both physical (for bitmap) and rotated (for coordinates)
        try:
            rotated_width = _display_cache['actual_display'].width if hasattr(_display_cache['actual_display'], 'width') else phys_height
            rotated_height = _display_cache['actual_display'].height if hasattr(_display_cache['actual_display'], 'height') else phys_width
            print(f"  Dimensions after rotation (for coordinates): {rotated_width}x{rotated_height}")
        except:
            # Fallback: manually swap
            rotated_width = phys_height  # 820
            rotated_height = phys_width  # 320
        
        # Use rotated dimensions for coordinate calculations
        _display_cache['width'] = rotated_width  # 820 for coordinate calculations
        _display_cache['height'] = rotated_height  # 320 for coordinate calculations
    
    return _display_cache['actual_display'], _display_cache['width'], _display_cache['height']

def display_speed(display_obj, speed_value):
    """Display speed on Qualia RGB666 TFT (optimized for high message rates)"""
    if not QUALIA_AVAILABLE or display_obj is None:
        return
    
    try:
        # Format speed as text
        speed_text = f"{int(speed_value)}"
        
        # Get cached display info
        actual_display, width, height = _get_display_info(display_obj)
        # After rotation: width=820 (full height), height=320
        
        # Use displayio for rendering
        import displayio
        from adafruit_display_text import label
        import terminalio
        
        # Reuse group if it exists, otherwise create new one
        if _display_cache['group'] is None:
            group = displayio.Group()
            
            # Create black background for HUD
            # Bitmap MUST use physical dimensions (320x820) even after rotation
            # Rotation affects the coordinate system, not the bitmap buffer size
            phys_width = _display_cache.get('phys_width', height)  # 320
            phys_height = _display_cache.get('phys_height', width)  # 820
            bitmap = displayio.Bitmap(phys_width, phys_height, 1)
            print(f"  Created bitmap: {phys_width}x{phys_height} (physical, for buffer)")
            palette = displayio.Palette(1)
            palette[0] = 0x000000  # Black background (HUD style)
            bg_tile = displayio.TileGrid(bitmap, pixel_shader=palette)
            group.append(bg_tile)
            
            # Create speed label (we'll update its text)
            # After 90° rotation + horizontal flip for HUD: coordinates are swapped and mirrored
            # Original: 320x820, After rotation: x goes 0-820, y goes 0-320
            # For HUD flip: if hardware flip doesn't work, we flip x coordinate manually
            # Center: x=width//2 (410), y=height//2 (160)
            # Scale up to use full width (820 pixels) for large text
            center_x = width//2  # 410 (center of rotated width)
            center_y = height//2  # 160 (center of rotated height)
            print(f"  Speed label at: ({center_x}, {center_y}), scale=20, bitmap={phys_width}x{phys_height}")
            print(f"  HUD mode: rotated 90°, horizontally flipped, vertically flipped, green text on black")
            
            # Create label at origin (will be flipped by group)
            speed_label = label.Label(
                terminalio.FONT, 
                text=speed_text, 
                color=0x00FF00,  # Green text (HUD style - classic HUD color)
                x=0,  # Position relative to flip group
                y=0,  # Position relative to flip group
                anchor_point=(0.5, 0.5),
                anchored_position=(0, 0),  # Center of flip group
                scale=18  # Large scale to use full width (820 pixels)
            )
            
            # Wrap label in a group with negative scale to flip upside down and mirror
            # For windshield reflection: text must be upside down (scale_y=-1) and mirrored (scale_x=-1)
            try:
                # Create group first, then set scale as property (CircuitPython may require this)
                flip_group = displayio.Group(x=center_x, y=center_y)
                flip_group.scale = (-1, -1)  # Set scale after creation: flip both axes
                flip_group.append(speed_label)
                group.append(flip_group)
                print(f"  Applied flip group: scale=(-1, -1) (upside down and mirrored)")
            except (TypeError, AttributeError) as e:
                print(f"  Group scale property not working ({e}), trying constructor...")
                try:
                    # Try setting scale in constructor
                    flip_group = displayio.Group(x=center_x, y=center_y, scale=(-1, -1))
                    flip_group.append(speed_label)
                    group.append(flip_group)
                    print(f"  Applied flip group via constructor: scale=(-1, -1)")
                except (TypeError, AttributeError) as e2:
                    print(f"  Constructor scale also failed ({e2}), trying Transform...")
                    try:
                        # Alternative: try Transform object
                        transform = displayio.Transform(scale_x=-1, scale_y=-1)
                        flip_group = displayio.Group(x=center_x, y=center_y)
                        if hasattr(flip_group, 'transform'):
                            flip_group.transform = transform
                        flip_group.append(speed_label)
                        group.append(flip_group)
                        print(f"  Applied transform: scale_x=-1, scale_y=-1")
                    except Exception as e3:
                        print(f"  All flip methods failed ({e3}), using direct label")
                        # Fallback: direct label (hardware flip should handle it)
                        speed_label.x = center_x
                        speed_label.y = center_y
                        speed_label.anchored_position = (center_x, center_y)
                        group.append(speed_label)
                        print(f"  Using direct label (relying on hardware flip)")
            
            # Store the label reference (not the group) for text updates
            _display_cache['speed_label'] = speed_label
            # Also store the group if we created one
            _display_cache['flip_group'] = flip_group if 'flip_group' in locals() else None
            
            # Create MPH label (static text, below speed)
            # mph_label = label.Label(
            #     terminalio.FONT, 
            #     text="MPH", 
            #     color=0x888888, 
            #     x=width//2,  # 410
            #     y=height//2 + 80,  # 160 + 80 = 240 (below speed, with more space)
            #     anchor_point=(0.5, 0.5),
            #     anchored_position=(width//2, height//2 + 80),
            #     scale=5  # Medium scale
            # )
            # group.append(mph_label)
            # _display_cache['mph_label'] = mph_label
            _display_cache['group'] = group
            
            # Set root group once
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
        else:
            # Just update the speed label text (much faster than recreating everything)
            # Only update if text actually changed (avoid unnecessary rendering)
            if _display_cache['speed_label'].text != speed_text:
                _display_cache['speed_label'].text = speed_text
        
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
            # Use displayio to show "IDLE" message (same approach as test)
            import displayio
            from adafruit_display_text import label
            import terminalio
            
            # Get the actual display object
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
            
            # Set rotation to 90 degrees + flip for HUD
            # HUD needs: rotated 90° + horizontal flip (mirror) + vertical flip (upside down)
            # This makes it readable when reflected in windshield
            try:
                if hasattr(actual_display, 'rotation'):
                    actual_display.rotation = 90
                    print("✓ Display rotated 90 degrees")
                
                # Enable horizontal flip (mirror left-right) for HUD
                if hasattr(actual_display, 'horizontal_flip'):
                    actual_display.horizontal_flip = True
                    print("✓ Horizontal flip enabled (HUD mirror)")
                elif hasattr(actual_display, 'flip_x'):
                    actual_display.flip_x = True
                    print("✓ flip_x enabled (HUD mirror)")
                elif hasattr(actual_display, 'mirror_x'):
                    actual_display.mirror_x = True
                    print("✓ mirror_x enabled (HUD mirror)")
                
                # Enable vertical flip (upside down) for HUD
                if hasattr(actual_display, 'vertical_flip'):
                    actual_display.vertical_flip = True
                    print("✓ Vertical flip enabled (upside down)")
                elif hasattr(actual_display, 'flip_y'):
                    actual_display.flip_y = True
                    print("✓ flip_y enabled (upside down)")
                elif hasattr(actual_display, 'mirror_y'):
                    actual_display.mirror_y = True
                    print("✓ mirror_y enabled (upside down)")
            except Exception as e:
                print(f"  Could not set rotation/flip: {e}")
            
            # Get dimensions BEFORE and AFTER rotation
            phys_width = actual_display.width if hasattr(actual_display, 'width') else 320
            phys_height = actual_display.height if hasattr(actual_display, 'height') else 820
            print(f"  Physical dimensions before rotation: {phys_width}x{phys_height}")
            
            # Get dimensions AFTER rotation
            if hasattr(actual_display, 'rotation'):
                # Get actual dimensions from rotated display
                width = actual_display.width if hasattr(actual_display, 'width') else phys_width
                height = actual_display.height if hasattr(actual_display, 'height') else phys_height
            else:
                # Rotation not supported, swap manually
                width = phys_height  # 820
                height = phys_width  # 320
            
            print(f"  Display dimensions after rotation: {width}x{height}")
            
            # Create group with "IDLE" text
            group = displayio.Group()
            
            # Black background
            # Bitmap MUST use physical dimensions (320x820) even after rotation
            # Rotation affects coordinate system, but bitmap buffer size is always physical
            # Get physical dimensions from before rotation
            phys_width = actual_display.width if hasattr(actual_display, 'width') else 320
            phys_height = actual_display.height if hasattr(actual_display, 'height') else 820
            
            # After rotation, these might be swapped - but for bitmap we need original physical size
            # If rotation swapped them, we need to un-swap for bitmap
            if hasattr(actual_display, 'rotation') and actual_display.rotation == 90:
                # Dimensions are swapped, use the larger one for width, smaller for height
                # Actually, let's check what the actual physical buffer size is
                bitmap = displayio.Bitmap(320, 820, 1)  # Always use physical: 320x820
                print(f"  Created bitmap: 320x820 (physical dimensions)")
            else:
                bitmap = displayio.Bitmap(phys_width, phys_height, 1)
                print(f"  Created bitmap: {phys_width}x{phys_height}")
            palette = displayio.Palette(1)
            palette[0] = 0x000000  # Black background (HUD style)
            bg_tile = displayio.TileGrid(bitmap, pixel_shader=palette)
            group.append(bg_tile)
            
            # "IDLE" text centered (green for HUD)
            center_x = width//2
            center_y = height//2
            print(f"  IDLE label at: ({center_x}, {center_y})")
            
            # Create IDLE label at origin (will be flipped by group)
            idle_label = label.Label(
                terminalio.FONT,
                text="IDLE",
                color=0x00FF00,  # Green text (HUD style)
                x=0,  # Position relative to flip group
                y=0,  # Position relative to flip group
                anchor_point=(0.5, 0.5),
                anchored_position=(0, 0),  # Center of flip group
                scale=15  # Large scale for full height
            )
            
            # Wrap label in a group with negative scale to flip upside down and mirror
            try:
                # Create group first, then set scale as property (CircuitPython may require this)
                flip_group = displayio.Group(x=center_x, y=center_y)
                flip_group.scale = (-1, -1)  # Set scale after creation: flip both axes
                flip_group.append(idle_label)
                group.append(flip_group)
                print(f"  Applied flip group to IDLE: scale=(-1, -1) (upside down and mirrored)")
            except (TypeError, AttributeError) as e:
                print(f"  IDLE group scale property not working ({e}), trying constructor...")
                try:
                    flip_group = displayio.Group(x=center_x, y=center_y, scale=(-1, -1))
                    flip_group.append(idle_label)
                    group.append(flip_group)
                    print(f"  Applied flip group to IDLE via constructor: scale=(-1, -1)")
                except (TypeError, AttributeError) as e2:
                    print(f"  IDLE constructor scale also failed ({e2}), trying transform...")
                    try:
                        transform = displayio.Transform(scale_x=-1, scale_y=-1)
                        flip_group = displayio.Group(x=center_x, y=center_y)
                        if hasattr(flip_group, 'transform'):
                            flip_group.transform = transform
                        flip_group.append(idle_label)
                        group.append(flip_group)
                        print(f"  Applied transform to IDLE")
                    except:
                        # Fallback: direct label
                        idle_label.x = center_x
                        idle_label.y = center_y
                        idle_label.anchored_position = (center_x, center_y)
                        group.append(idle_label)
                        print(f"  Using direct IDLE label (relying on hardware flip)")
            
            # Set root group
            if hasattr(actual_display, 'root_group'):
                actual_display.root_group = group
            elif hasattr(display, 'root_group'):
                display.root_group = group
            else:
                try:
                    import board
                    board.DISPLAY.root_group = group
                except:
                    pass
            
            print("✓ Qualia RGB666 TFT initialized")
            print("✓ 'IDLE' message displayed - if you see this on the display, hardware is working!")
            
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
    
    # CircuitPython: Read from USB serial (non-blocking, optimized for high message rates)
    # Use supervisor to check for available bytes
    buffer = ""
    line_count = 0
    last_display_update = 0
    display_update_interval = 0.1  # Update display at most every 100ms (10fps max) - slower for large text
    pending_speed = None
    last_speed = None  # Track if speed actually changed
    
    # Optimize: Read chunks instead of character-by-character
    while True:
        try:
            # Check if data is available (CircuitPython way)
            if supervisor.runtime.serial_bytes_available:
                # Read in larger chunks when possible
                chunk_size = min(supervisor.runtime.serial_bytes_available, 256)
                try:
                    chunk = sys.stdin.read(chunk_size)
                    if chunk:
                        buffer += chunk
                except OSError:
                    pass
                
                # Process all complete lines in buffer (don't block on display updates)
                lines_to_process = []
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    line = line.strip()
                    if line:
                        lines_to_process.append(line)
                
                # Process lines - only keep the latest speed value if multiple arrive
                for line in lines_to_process:
                    line_count += 1
                    try:
                        speed = float(line)
                        # Only update if speed actually changed (skip redundant updates)
                        if speed != pending_speed:
                            pending_speed = speed
                        if line_count % 10 == 0:  # Only log every 10th message
                            print(f"[{line_count}] Received: {speed} MPH")
                    except ValueError:
                        if line_count % 10 == 0:
                            print(f"[{line_count}] Invalid: '{line}'")
                
                # Throttle display updates (don't update faster than display can handle)
                # Also only update if speed actually changed
                current_time = time.monotonic()
                time_since_update = current_time - last_display_update
                if pending_speed is not None and pending_speed != last_speed and time_since_update >= display_update_interval:
                    display_speed(display, pending_speed)
                    last_display_update = current_time
                    last_speed = pending_speed  # Track what we displayed
                    pending_speed = None  # Clear after displaying
                    
            else:
                # No data available, check if we need to update display with pending value
                if pending_speed is not None and pending_speed != last_speed:
                    current_time = time.monotonic()
                    if (current_time - last_display_update) >= display_update_interval:
                        display_speed(display, pending_speed)
                        last_display_update = current_time
                        last_speed = pending_speed
                        pending_speed = None
                # Small delay when no data
                time.sleep(0.01)
                
        except KeyboardInterrupt:
            print("\n\nStopping...")
            if display:
                try:
                    # Clear display using displayio
                    import displayio
                    clear_group = displayio.Group()
                    bg_bitmap = displayio.Bitmap(width, height, 1)
                    bg_palette = displayio.Palette(1)
                    bg_palette[0] = 0x000000
                    bg_tile = displayio.TileGrid(bg_bitmap, pixel_shader=bg_palette)
                    clear_group.append(bg_tile)
                    if hasattr(actual_display, 'root_group'):
                        actual_display.root_group = clear_group
                    elif hasattr(display, 'root_group'):
                        display.root_group = clear_group
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


# CircuitPython automatically runs code.py on boot, so call main() directly
main()
