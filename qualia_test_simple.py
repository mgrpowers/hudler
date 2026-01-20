"""
Even simpler test - just show colors
Upload this as main.py to ESP32-S3

First, install the Qualia library:
- Download from: https://circuitpython.org/libraries
- Copy adafruit_qualia folder to CIRCUITPY/lib/
"""

import time

# Try different possible import names
display = None

# Try Option 1: Direct import from displays folder (bypass submodule issues)
# Your display is: 3.2" 320x820 bar display (TL032FWV01CT-I1440A)
try:
    # Import directly from the file path
    import sys
    sys.path.insert(0, '/lib/adafruit_qualia/displays')
    
    # Try importing bar320x820 directly
    import bar320x820
    print(f"  bar320x820 module loaded, contents: {[x for x in dir(bar320x820) if not x.startswith('_')][:10]}")
    
    # Try different instantiation patterns
    if hasattr(bar320x820, 'Bar320x820'):
        # Try without arguments first
        try:
            display = bar320x820.Bar320x820()
            print("✓ Loaded: Bar320x820() - no arguments")
        except TypeError as e:
            print(f"  Bar320x820() failed: {e}")
            # Try with board if available
            try:
                import board
                if hasattr(board, 'DISPLAY'):
                    display = bar320x820.Bar320x820(board.DISPLAY)
                    print("✓ Loaded: Bar320x820(board.DISPLAY)")
                else:
                    # Try with other common board attributes
                    for attr in ['I2C', 'SPI', 'UART']:
                        if hasattr(board, attr):
                            try:
                                display = bar320x820.Bar320x820(getattr(board, attr))
                                print(f"✓ Loaded: Bar320x820(board.{attr})")
                                break
                            except:
                                continue
            except ImportError:
                print("  board module not available")
    else:
        print(f"  Bar320x820 class not found in module")
        # List what's available
        print(f"  Available: {[x for x in dir(bar320x820) if not x.startswith('_')]}")
except Exception as e:
    print(f"  Direct bar320x820 import failed: {e}")
    import sys
    try:
        sys.print_exception(e)
    except:
        pass
    pass

# Try Option 2: adafruit_qualia.Qualia (but board.DISPLAY might not exist)
if display is None:
    try:
        from adafruit_qualia import Qualia
        
        # Try without board.DISPLAY first (maybe it's optional or auto-detected)
        patterns = [
            ("bar320x820",),  # Just display type
            ("round40",),
            ("square40",),
        ]
        
        for pattern in patterns:
            try:
                display = Qualia(*pattern)
                print(f"✓ Loaded: Qualia{pattern} (no board.DISPLAY)")
                break
            except (TypeError, ValueError, AttributeError) as e:
                print(f"  Qualia{pattern} failed: {type(e).__name__}: {e}")
                continue
        
        # Try with board if it exists
        if display is None:
            try:
                import board
                if hasattr(board, 'DISPLAY'):
                    patterns_with_board = [
                        (board.DISPLAY, "bar320x820"),
                        (board.DISPLAY, "round40"),
                        ("bar320x820", board.DISPLAY),
                    ]
                    for pattern in patterns_with_board:
                        try:
                            display = Qualia(*pattern)
                            print(f"✓ Loaded: Qualia{pattern}")
                            break
                        except (TypeError, ValueError, AttributeError) as e:
                            print(f"  Qualia{pattern} failed: {type(e).__name__}: {e}")
                            continue
                else:
                    print("  board.DISPLAY not available (this is OK for Qualia)")
            except ImportError:
                print("  board module not available")
    except (ImportError, TypeError, AttributeError) as e:
        print(f"  Qualia() import/init failed: {e}")
    
    # If all patterns failed, try to inspect what Qualia needs
    if display is None:
        try:
            from adafruit_qualia import Qualia
            print("\n  All patterns failed. Checking Qualia requirements...")
            try:
                import inspect
                sig = inspect.signature(Qualia)
                print(f"  Qualia signature: {sig}")
            except Exception as e:
                print(f"  Cannot inspect signature: {e}")
                # Try to see the __init__ method
                try:
                    if hasattr(Qualia, '__init__'):
                        print(f"  Qualia has __init__ method")
                        # Try to get docstring
                        if hasattr(Qualia.__init__, '__doc__'):
                            print(f"  Docstring: {Qualia.__init__.__doc__}")
                except:
                    pass
        except:
            pass

# This is now handled in Option 1 above

# Try Option 2: qualia
if display is None:
    try:
        from qualia import Qualia
        display = Qualia()
        print("✓ Loaded: from qualia import Qualia")
    except ImportError:
        pass

# Try Option 3: qualia_esp32s3
if display is None:
    try:
        from qualia_esp32s3 import Qualia
        display = Qualia()
        print("✓ Loaded: from qualia_esp32s3 import Qualia")
    except ImportError:
        pass

if display is None:
    print("\n✗ Qualia library not found!")
    print("\nDiagnosing...")
    
    # Check if lib folder exists and what's in it
    try:
        import os
        lib_path = '/lib'
        if os.path.exists(lib_path):
            print(f"✓ /lib folder exists")
            try:
                contents = os.listdir(lib_path)
                print(f"  Contents: {contents}")
                if 'adafruit_qualia' in contents:
                    print("  ✓ adafruit_qualia folder found!")
                    qualia_path = lib_path + '/adafruit_qualia'
                    try:
                        qualia_files = os.listdir(qualia_path)
                        print(f"  Files in adafruit_qualia: {qualia_files[:10]}")
                    except Exception as e:
                        print(f"  Error reading adafruit_qualia: {e}")
            except Exception as e:
                print(f"  Error listing /lib: {e}")
        else:
            print(f"✗ /lib folder not found")
    except Exception as e:
        print(f"Error checking filesystem: {e}")
    
    # Try to see what modules are available
    try:
        import sys
        print("\nChecking sys.path:")
        for path in sys.path:
            print(f"  {path}")
    except:
        pass
    
    # Try importing the module directly to see the actual error
    print("\nTrying direct import to see error:")
    try:
        import adafruit_qualia
        print("  ✓ import adafruit_qualia worked!")
        print(f"  Available: {dir(adafruit_qualia)[:15]}")
        
        # Try displays submodule - check if it's accessible
        try:
            # Try direct attribute access
            if hasattr(adafruit_qualia, 'displays'):
                displays = adafruit_qualia.displays
                print("  ✓ adafruit_qualia.displays available")
                print(f"  Displays contents: {dir(displays)[:15]}")
            else:
                print("  ✗ displays attribute not found in adafruit_qualia")
                # Try importing it
                try:
                    import adafruit_qualia.displays
                    print("  ✓ adafruit_qualia.displays import worked")
                except ImportError:
                    print("  ✗ Cannot import displays submodule")
        except Exception as e:
            print(f"  ✗ Error checking displays: {e}")
            
    except ImportError as e:
        print(f"  ✗ Import error: {e}")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    print("\nTo fix:")
    print("1. Make sure adafruit_qualia folder is in /lib/")
    print("2. Check that it contains __init__.py or __init__.mpy")
    print("3. Restart ESP32-S3 after copying files")
    print("4. Check CircuitPython version matches library version")
else:
    print("Display initialized!")
    
    # Check what attributes Qualia has
    print(f"Qualia attributes: {[x for x in dir(display) if not x.startswith('_')][:20]}")
    
    # Try to get the actual display object
    actual_display = None
    if hasattr(display, 'display'):
        actual_display = display.display
        print(f"Found display.display attribute")
    elif hasattr(display, '_display'):
        actual_display = display._display
        print(f"Found display._display attribute")
    elif hasattr(display, 'root_group'):
        # It might be a displayio display itself
        actual_display = display
        print(f"Using display directly as displayio object")
    else:
        # Try to access via board.DISPLAY
        try:
            import board
            actual_display = board.DISPLAY
            print(f"Using board.DISPLAY")
        except:
            actual_display = display
            print(f"Using Qualia object directly")
    
    # Cycle through colors using displayio
    import displayio
    colors = [
        (0xFF0000, "RED"),
        (0x00FF00, "GREEN"),
        (0x0000FF, "BLUE"),
        (0xFFFFFF, "WHITE"),
        (0x000000, "BLACK")
    ]
    
    # Get display dimensions
    try:
        width = actual_display.width if hasattr(actual_display, 'width') else 320
        height = actual_display.height if hasattr(actual_display, 'height') else 820
        print(f"Display size: {width}x{height}")
    except:
        width, height = 320, 820
        print(f"Using default size: {width}x{height}")
    
    while True:
        for color, name in colors:
            print(f"Showing {name}...")
            try:
                # Create a bitmap filled with the color
                bitmap = displayio.Bitmap(width, height, 1)
                palette = displayio.Palette(1)
                palette[0] = color
                tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)
                
                # Create a group and set it as root
                group = displayio.Group()
                group.append(tile_grid)
                
                # Set root group on the display
                if hasattr(actual_display, 'root_group'):
                    actual_display.root_group = group
                elif hasattr(display, 'root_group'):
                    display.root_group = group
                else:
                    # Try to set on board.DISPLAY
                    try:
                        import board
                        board.DISPLAY.root_group = group
                    except:
                        print(f"  Could not set root_group")
                        
            except Exception as e:
                print(f"  Display error: {e}")
                import sys
                try:
                    sys.print_exception(e)
                except:
                    pass
            time.sleep(2)
