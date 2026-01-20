"""
TFT35" Display Interface
Handles initialization and rendering for TFT35" touch shield
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Try to import display libraries - support multiple approaches
try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logger.warning("PIL/Pillow not available")

# Framebuffer access will be checked by testing if device exists

# Try SPI-based display (ILI9486 or similar)
try:
    import spidev
    import RPi.GPIO as GPIO
    SPI_AVAILABLE = True
except ImportError:
    SPI_AVAILABLE = False
    logger.warning("RPi.GPIO or spidev not available - running in simulation mode")

# Try serial for Pico communication
try:
    import serial
    import serial.tools.list_ports
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    logger.warning("pyserial not available - Pico display will not work")


class TFTDisplay:
    """Interface for TFT35" display rendering"""
    
    def __init__(self):
        self.width = 480
        self.height = 320
        self.current_speed: Optional[float] = None
        self.display_mode = self._detect_display_mode()
        self._init_display()
        logger.info(f"Display initialized using {self.display_mode} mode")
    
    def _detect_display_mode(self) -> str:
        """Detect available display rendering method"""
        # Check for framebuffer device (most common for TFT35")
        fb_device = os.getenv('FRAMEBUFFER', '/dev/fb1')
        if os.path.exists(fb_device):
            return 'framebuffer'
        
        # Fall back to PIL-based rendering (can use framebuffer or SPI)
        if PIL_AVAILABLE:
            return 'pil'
        
        # Simulation mode if nothing available
        return 'simulation'
    
    def _init_display(self):
        """Initialize display based on detected mode"""
        if self.display_mode == 'framebuffer':
            self._init_framebuffer()
        elif self.display_mode == 'pil':
            self._init_pil()
        else:
            logger.warning("Running in simulation mode - no display output")
    
    def _init_framebuffer(self):
        """Initialize framebuffer-based display"""
        try:
            fb_device = os.getenv('FRAMEBUFFER', '/dev/fb1')
            # Test if we can open the framebuffer
            self.fb = open(fb_device, 'wb')
            logger.info(f"Framebuffer opened: {fb_device}")
        except PermissionError:
            logger.error(f"Permission denied accessing {fb_device}. Try running with sudo.")
            self.display_mode = 'simulation'
        except FileNotFoundError:
            logger.warning(f"Framebuffer device {fb_device} not found. Using simulation mode.")
            self.display_mode = 'simulation'
        except Exception as e:
            logger.error(f"Failed to open framebuffer: {e}")
            self.display_mode = 'simulation'
    
    def _init_pil(self):
        """Initialize PIL-based rendering"""
        if not PIL_AVAILABLE:
            self.display_mode = 'simulation'
            return
        
        # Create initial image
        self.image = Image.new('RGB', (self.width, self.height), color=(0, 0, 0))
        self.draw = ImageDraw.Draw(self.image)
        
        # Try to load a large font
        self.font_path = None
        try:
            # Try to use a system font
            font_paths = [
                '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
                '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
                '/System/Library/Fonts/Helvetica.ttc',
            ]
            self.font = None
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        self.font = ImageFont.truetype(font_path, 120)
                        self.font_path = font_path
                        logger.info(f"Loaded font: {font_path}")
                        break
                    except:
                        continue
            
            if self.font is None:
                # Fall back to default font
                self.font = ImageFont.load_default()
                logger.warning("Using default font (may be small)")
        except Exception as e:
            logger.warning(f"Font loading error: {e}, using default")
            self.font = ImageFont.load_default()
    
    def update_speed(self, speed: float):
        """Update display with new speed value in MPH"""
        self.current_speed = speed
        
        if self.display_mode == 'framebuffer':
            self._render_framebuffer(speed)
        elif self.display_mode == 'pil':
            self._render_pil(speed)
        else:
            # Simulation mode - just log
            logger.info(f"[SIMULATION] Speed: {speed} MPH")
    
    def _render_framebuffer(self, speed: float):
        """Render to framebuffer"""
        if not PIL_AVAILABLE:
            return
        
        # Create image
        image = Image.new('RGB', (self.width, self.height), color=(0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Draw speed text
        speed_text = f"{int(speed):d}"
        mph_text = "MPH"
        
        # Calculate text positions (centered)
        if hasattr(self, 'font') and self.font:
            # Get text bounding boxes
            bbox_speed = draw.textbbox((0, 0), speed_text, font=self.font)
            bbox_mph = draw.textbbox((0, 0), mph_text, font=self.font)
            
            text_width_speed = bbox_speed[2] - bbox_speed[0]
            text_height_speed = bbox_speed[3] - bbox_speed[1]
            text_width_mph = bbox_mph[2] - bbox_mph[0]
            text_height_mph = bbox_mph[3] - bbox_mph[1]
            
            # Center speed
            x_speed = (self.width - text_width_speed) // 2
            y_speed = (self.height - text_height_speed - text_height_mph - 20) // 2
            
            # Center MPH below speed
            x_mph = (self.width - text_width_mph) // 2
            y_mph = y_speed + text_height_speed + 20
        else:
            # Default positioning if no font
            x_speed = self.width // 2
            y_speed = self.height // 2 - 20
            x_mph = self.width // 2
            y_mph = self.height // 2 + 20
        
        # Draw text in white
        draw.text((x_speed, y_speed), speed_text, font=self.font if hasattr(self, 'font') else None, fill=(255, 255, 255))
        
        # Use smaller font for MPH label
        try:
            if hasattr(self, 'font_path') and self.font_path and self.font:
                mph_font_size = int(120 * 0.4)  # Use base size calculation
                mph_font = ImageFont.truetype(self.font_path, mph_font_size)
                draw.text((x_mph, y_mph), mph_text, font=mph_font, fill=(200, 200, 200))
            else:
                draw.text((x_mph, y_mph), mph_text, fill=(200, 200, 200))
        except Exception as e:
            logger.debug(f"Could not use custom font for MPH label: {e}")
            draw.text((x_mph, y_mph), mph_text, fill=(200, 200, 200))
        
        # Convert to RGB565 format for framebuffer
        try:
            # Convert PIL image to RGB565 bytes
            pixels = image.tobytes('raw', 'RGB')
            rgb565_data = bytearray(self.width * self.height * 2)
            
            for i in range(self.width * self.height):
                r = pixels[i * 3]
                g = pixels[i * 3 + 1]
                b = pixels[i * 3 + 2]
                
                # Convert RGB888 to RGB565
                rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
                rgb565_data[i * 2] = rgb565 & 0xFF
                rgb565_data[i * 2 + 1] = (rgb565 >> 8) & 0xFF
            
            # Write to framebuffer
            if hasattr(self, 'fb') and self.fb:
                self.fb.seek(0)
                self.fb.write(rgb565_data)
                self.fb.flush()
        except Exception as e:
            logger.error(f"Framebuffer write error: {e}")
    
    def _render_pil(self, speed: float):
        """Render using PIL (for SPI displays or alternative methods)"""
        if not PIL_AVAILABLE:
            return
        
        # Clear image
        self.draw.rectangle([(0, 0), (self.width, self.height)], fill=(0, 0, 0))
        
        # Draw speed text
        speed_text = f"{int(speed):d}"
        mph_text = "MPH"
        
        # Calculate centered positions
        if hasattr(self, 'font') and self.font:
            bbox_speed = self.draw.textbbox((0, 0), speed_text, font=self.font)
            text_width_speed = bbox_speed[2] - bbox_speed[0]
            text_height_speed = bbox_speed[3] - bbox_speed[1]
            
            x_speed = (self.width - text_width_speed) // 2
            y_speed = (self.height - text_height_speed) // 2 - 40
        else:
            x_speed = self.width // 2
            y_speed = self.height // 2 - 40
        
        # Draw speed (white, large)
        self.draw.text(
            (x_speed, y_speed), 
            speed_text, 
            font=self.font if hasattr(self, 'font') else None,
            fill=(255, 255, 255)
        )
        
        # Draw MPH label (gray, smaller)
        mph_font = None
        if hasattr(self, 'font_path') and self.font_path:
            try:
                mph_size = int(120 * 0.4)  # Use base size calculation
                mph_font = ImageFont.truetype(self.font_path, mph_size)
            except:
                mph_font = self.font
        elif hasattr(self, 'font') and self.font:
            mph_font = self.font
        
        mph_bbox = self.draw.textbbox((0, 0), mph_text, font=mph_font) if mph_font else None
        if mph_bbox:
            x_mph = (self.width - (mph_bbox[2] - mph_bbox[0])) // 2
            y_mph = y_speed + text_height_speed + 20
        else:
            x_mph = self.width // 2
            y_mph = y_speed + 100
        
        self.draw.text((x_mph, y_mph), mph_text, font=mph_font, fill=(200, 200, 200))
        
        # For PIL mode, if SPI is available, you could send to SPI here
        # For now, this would need to be extended based on specific display hardware
        logger.debug(f"PIL render: {speed} MPH")
    
    def cleanup(self):
        """Clean up display resources"""
        if hasattr(self, 'fb') and self.fb:
            try:
                self.fb.close()
            except:
                pass
        logger.info("Display cleanup complete")


class PicoScrollDisplay:
    """Interface for Pimoroni Pico Scroll display via USB serial"""
    
    def __init__(self, port=None, baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.current_speed: Optional[float] = None
        self.ser = None
        self._init_serial()
    
    def _find_pico_port(self):
        """Find the serial port for Raspberry Pi Pico"""
        if self.port:
            return self.port
        
        # Check environment variable
        env_port = os.getenv('PICO_SERIAL_PORT')
        if env_port:
            logger.info(f"Using Pico port from environment: {env_port}")
            return env_port
        
        if not SERIAL_AVAILABLE:
            return None
        
        # Auto-detect Pico
        try:
            ports = serial.tools.list_ports.comports()
            pico_identifiers = ['Pico', 'pico', 'Raspberry Pi Pico', 'RPI', 'USB Serial']
            
            for port in ports:
                # Check description
                if any(identifier in port.description for identifier in pico_identifiers):
                    logger.info(f"Auto-detected Pico: {port.device}")
                    return port.device
                
                # Check VID/PID (Raspberry Pi Foundation VID is 0x2E8A)
                if hasattr(port, 'vid') and port.vid == 0x2E8A:
                    logger.info(f"Auto-detected Pico by VID: {port.device}")
                    return port.device
        except Exception as e:
            logger.warning(f"Error detecting Pico port: {e}")
        
        return None
    
    def _init_serial(self):
        """Initialize serial connection to Pico"""
        if not SERIAL_AVAILABLE:
            logger.error("pyserial not available. Install with: pip install pyserial")
            return
        
        port_name = self._find_pico_port()
        if not port_name:
            logger.error("No Pico serial port found!")
            logger.info("Please connect your Pico and try again.")
            logger.info("Or set PICO_SERIAL_PORT environment variable.")
            return
        
        try:
            logger.info(f"Connecting to Pico at {port_name} ({self.baudrate} baud)...")
            self.ser = serial.Serial(port_name, self.baudrate, timeout=1)
            import time
            time.sleep(2)  # Give Pico time to initialize
            logger.info("Pico serial connection established!")
            self.port = port_name
        except serial.SerialException as e:
            logger.error(f"Failed to open serial port {port_name}: {e}")
            logger.info("Make sure Pico is connected and not in use by another program")
            self.ser = None
        except Exception as e:
            logger.error(f"Unexpected error opening serial port: {e}")
            self.ser = None
    
    def update_speed(self, speed: float):
        """Send speed update to Pico over serial
        
        Sends speed as a number with newline, matching the format expected by
        the Pico code (simpletest.py) which reads from stdin and displays using
        picoscroll.show_text()
        """
        self.current_speed = speed
        
        if not self.ser:
            logger.warning("Serial port not available - cannot send to Pico")
            return
        
        try:
            # Send speed as simple number with newline
            # Format: "65\n" for 65 MPH
            # The Pico code will format it as "65 MPH" and display using show_text()
            msg = f"{int(speed)}\n"
            self.ser.write(msg.encode('utf-8'))
            self.ser.flush()  # Ensure data is sent immediately
            logger.debug(f"Sent to Pico: {speed} MPH")
        except serial.SerialException as e:
            logger.error(f"Serial write error: {e}")
            # Try to reconnect
            self._reconnect()
        except Exception as e:
            logger.error(f"Error sending to Pico: {e}")
    
    def _reconnect(self):
        """Attempt to reconnect to Pico"""
        logger.info("Attempting to reconnect to Pico...")
        if self.ser:
            try:
                self.ser.close()
            except:
                pass
            self.ser = None
        
        import time
        time.sleep(1)
        self._init_serial()
    
    def cleanup(self):
        """Clean up serial connection"""
        if self.ser:
            try:
                self.ser.close()
                logger.info("Pico serial connection closed")
            except:
                pass
            self.ser = None


class QualiaESP32Display:
    """Interface for Qualia ESP32-S3 RGB666 TFT display via USB serial"""
    
    def __init__(self, port=None, baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.current_speed: Optional[float] = None
        self.ser = None
        self._init_serial()
    
    def _find_esp32_port(self):
        """Find the serial port for ESP32-S3"""
        if self.port:
            return self.port
        
        # Check environment variable
        env_port = os.getenv('ESP32_SERIAL_PORT')
        if env_port:
            logger.info(f"Using ESP32 port from environment: {env_port}")
            return env_port
        
        if not SERIAL_AVAILABLE:
            return None
        
        # Auto-detect ESP32
        try:
            ports = serial.tools.list_ports.comports()
            esp32_identifiers = ['ESP32', 'ESP32-S3', 'CH340', 'CP210', 'Silicon Labs', 'USB Serial']
            
            for port in ports:
                # Check description
                if any(identifier in port.description for identifier in esp32_identifiers):
                    logger.info(f"Auto-detected ESP32: {port.device}")
                    return port.device
                
                # Check VID/PID (common ESP32 USB-to-Serial chip VIDs)
                # CH340: 0x1A86, CP210x: 0x10C4, Silicon Labs: 0x10C4, ESP32-S3: 0x303A
                if hasattr(port, 'vid'):
                    if port.vid in [0x1A86, 0x10C4, 0x303A]:
                        logger.info(f"Auto-detected ESP32 by VID: {port.device}")
                        return port.device
        except Exception as e:
            logger.warning(f"Error detecting ESP32 port: {e}")
        
        return None
    
    def _init_serial(self):
        """Initialize serial connection to ESP32"""
        if not SERIAL_AVAILABLE:
            logger.error("pyserial not available. Install with: pip install pyserial")
            return
        
        port_name = self._find_esp32_port()
        if not port_name:
            logger.error("No ESP32 serial port found!")
            logger.info("Please connect your ESP32-S3 and try again.")
            logger.info("Or set ESP32_SERIAL_PORT environment variable.")
            return
        
        try:
            logger.info(f"Connecting to ESP32-S3 at {port_name} ({self.baudrate} baud)...")
            self.ser = serial.Serial(port_name, self.baudrate, timeout=1)
            import time
            time.sleep(2)  # Give ESP32 time to initialize
            logger.info("ESP32-S3 serial connection established!")
            self.port = port_name
        except serial.SerialException as e:
            logger.error(f"Failed to open serial port {port_name}: {e}")
            logger.info("Make sure ESP32-S3 is connected and not in use by another program")
            self.ser = None
        except Exception as e:
            logger.error(f"Unexpected error opening serial port: {e}")
            self.ser = None
    
    def update_speed(self, speed: float):
        """Send speed update to ESP32-S3 over serial
        
        Sends speed as a number with newline, matching the format expected by
        the ESP32 code which reads from serial and displays on RGB666 TFT
        """
        self.current_speed = speed
        
        if not self.ser:
            logger.warning("Serial port not available - cannot send to ESP32-S3")
            return
        
        try:
            # Send speed as simple number with newline
            # Format: "65\n" for 65 MPH
            # The ESP32 code will format and display it on the RGB666 TFT
            msg = f"{int(speed)}\n"
            self.ser.write(msg.encode('utf-8'))
            self.ser.flush()  # Ensure data is sent immediately
            logger.debug(f"Sent to ESP32-S3: {speed} MPH")
        except serial.SerialException as e:
            logger.error(f"Serial write error: {e}")
            # Try to reconnect
            self._reconnect()
        except Exception as e:
            logger.error(f"Error sending to ESP32-S3: {e}")
    
    def _reconnect(self):
        """Attempt to reconnect to ESP32-S3"""
        logger.info("Attempting to reconnect to ESP32-S3...")
        if self.ser:
            try:
                self.ser.close()
            except:
                pass
            self.ser = None
        
        import time
        time.sleep(1)
        self._init_serial()
    
    def cleanup(self):
        """Clean up serial connection"""
        if self.ser:
            try:
                self.ser.close()
                logger.info("ESP32-S3 serial connection closed")
            except:
                pass
            self.ser = None

