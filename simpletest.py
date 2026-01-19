import time
from picoscroll import PicoScroll
import picoscroll
import sys
import uselect
from picographics import PicoGraphics, PEN_1BIT

picoscroll = PicoScroll()

SCROLL_WIDTH = 17
SCROLL_HEIGHT = 7

scroll = PicoScroll()

display = PicoGraphics(PEN_1BIT, SCROLL_WIDTH, SCROLL_HEIGHT)


def display_static_text(text_to_display, x_coord, y_coord):
    print('display static text')
    display.set_pen(1) # Set pen to white (or any non-zero value for on)
    display.clear()
    display.set_font("bitmap8") # Clear the display buffer
    # display.text(text_to_display, x_coord, y_coord, 1) # Draw the text
    picoscroll.clear()
    picoscroll.show_text(text_to_display, 8, -3)
    picoscroll.show()
    print('ostensibly showing text')
    display.update()   


def display_text(scroll_obj, text, clear_first=True):    
    try:
        # Clear display first
        if clear_first:
            try:
                scroll_obj.clear()
            except AttributeError:
                pass  # clear() might not exist, that's okay
        
        scroll.scroll_text(text, 128, 80)
        
    except Exception as e:
        print(f"Display error: {e}")
        import sys
        try:
            sys.print_exception(e)
        except:
            pass


def display_speed(scroll_obj, speed_value):

    
    # Format speed as text with "MPH" label
    speed_text = f"{int(speed_value)} MPH"
    display_static_text(speed_text, 1, 1)


while True:
    scroll_obj = None
    print("Displaying 'IDLE' message...")
    #display_static_text("Hello", 1, 1)
    word = "Hi"

    
    picoscroll.show_text(word, 8, 0)
    picoscroll.show()
    
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
                                display_speed(scroll_obj, speed)
                            except ValueError:
                                print(f"  → Not a number, ignoring")
            else:
                # No data available, small delay
                time.sleep(0.01)
                
        except KeyboardInterrupt:
            print("\n\nStopping...")
            if scroll_obj:
                try:
                    if hasattr(scroll_obj, 'clear'):
                        scroll_obj.clear()
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
    
    time.sleep(1)

