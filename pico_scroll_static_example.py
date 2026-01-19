"""
Example showing how to display STATIC text on Pico Scroll
This uses show_bitmap_1d() method for true static display

Note: This requires creating a font bitmap map. For simpler use,
you can try the scroll_text() method with offset=0 or use write_string() if available.
"""

import time
import picoscroll as scroll

# Simple 5x7 font bitmap for numbers and basic text
# Each character is 5 columns wide, stored as bytes
FONT_5x7 = {
    '0': [0x0E, 0x11, 0x11, 0x11, 0x0E],
    '1': [0x04, 0x0C, 0x04, 0x04, 0x0E],
    '2': [0x0E, 0x11, 0x02, 0x04, 0x1F],
    '3': [0x0E, 0x11, 0x06, 0x11, 0x0E],
    '4': [0x02, 0x06, 0x0A, 0x1F, 0x02],
    '5': [0x1F, 0x10, 0x0E, 0x01, 0x1E],
    '6': [0x0E, 0x10, 0x1E, 0x11, 0x0E],
    '7': [0x1F, 0x01, 0x02, 0x04, 0x08],
    '8': [0x0E, 0x11, 0x0E, 0x11, 0x0E],
    '9': [0x0E, 0x11, 0x0F, 0x01, 0x0E],
    ' ': [0x00, 0x00, 0x00, 0x00, 0x00],
    'I': [0x0E, 0x04, 0x04, 0x04, 0x0E],
    'D': [0x1C, 0x12, 0x11, 0x12, 0x1C],
    'L': [0x10, 0x10, 0x10, 0x10, 0x1F],
    'E': [0x1F, 0x10, 0x1E, 0x10, 0x1F],
    'M': [0x11, 0x1B, 0x15, 0x11, 0x11],
    'P': [0x1E, 0x11, 0x1E, 0x10, 0x10],
    'H': [0x11, 0x11, 0x1F, 0x11, 0x11],
}

def text_to_bitmap(text):
    """Convert text string to bitmap bytearray for Pico Scroll"""
    bitmap = bytearray()
    for char in text.upper():
        if char in FONT_5x7:
            # Add character columns
            for col in FONT_5x7[char]:
                bitmap.append(col)
            # Add 1 pixel spacing between characters
            bitmap.append(0x00)
        else:
            # Unknown character, use space
            for _ in range(6):  # 5 columns + 1 spacing
                bitmap.append(0x00)
    return bitmap

def display_static_text(text):
    """Display static (non-scrolling) text on Pico Scroll"""
    scroll.init()
    scroll.clear()
    
    # Convert text to bitmap
    bitmap = text_to_bitmap(text)
    
    # Display width is 17 pixels for Pico Scroll
    display_width = 17
    
    # Calculate offset to center text (optional)
    text_width = len(bitmap)
    if text_width < display_width:
        # Center the text
        offset = (display_width - text_width) // 2
    else:
        # Text is wider than display, start at 0
        offset = 0
    
    # Show bitmap at fixed offset (static display)
    scroll.show_bitmap_1d(bitmap, display_width, offset)
    scroll.update()

# Example usage
if __name__ == "__main__":
    scroll.init()
    
    # Display "IDLE" statically
    display_static_text("IDLE")
    print("Displaying 'IDLE' statically")
    time.sleep(3)
    
    # Display speed statically
    display_static_text("65")
    print("Displaying '65' statically")
    time.sleep(3)
    
    # Display "65 MPH" (might be too wide, will show what fits)
    display_static_text("65 MPH")
    print("Displaying '65 MPH' statically")
    time.sleep(3)

