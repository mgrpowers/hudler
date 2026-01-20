#!/usr/bin/env python3
"""
Test script for Mac/Raspberry Pi → ESP32-S3 serial communication
Tests near real-time message sending over USB serial to Qualia ESP32-S3 RGB666 TFT
"""

import serial
import serial.tools.list_ports
import time
import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def find_esp32_port():
    """Find the serial port for ESP32-S3"""
    ports = serial.tools.list_ports.comports()
    
    # Common identifiers for ESP32-S3
    esp32_identifiers = ['ESP32', 'ESP32-S3', 'CH340', 'CP210', 'Silicon Labs', 'USB Serial']
    
    for port in ports:
        logger.info(f"Found port: {port.device} - {port.description}")
        # Check if it looks like an ESP32
        if any(identifier in port.description for identifier in esp32_identifiers):
            logger.info(f"Potential ESP32-S3 found: {port.device}")
            return port.device
        
        # Also check VID/PID if available
        # CH340: 0x1A86, CP210x: 0x10C4, ESP32-S3: 0x303A
        if hasattr(port, 'vid') and hasattr(port, 'pid'):
            if port.vid in [0x1A86, 0x10C4, 0x303A]:  # Common ESP32 USB-to-Serial chips
                logger.info(f"ESP32-S3 found by VID: {port.device}")
                return port.device
    
    return None


def test_serial_communication(port_name=None, baudrate=115200):
    """Test sending messages to ESP32-S3 over serial"""
    
    if port_name is None:
        port_name = find_esp32_port()
    
    if port_name is None:
        logger.error("No ESP32-S3 serial port found!")
        logger.info("\nPlease connect your ESP32-S3 and try again.")
        logger.info("Or specify the port manually: python test_esp32_serial.py /dev/ttyUSB0")
        return False
    
    try:
        logger.info(f"Opening serial connection to {port_name} at {baudrate} baud...")
        ser = serial.Serial(port_name, baudrate, timeout=1)
        time.sleep(2)  # Give ESP32-S3 time to initialize
        
        logger.info("Serial connection established!")
        logger.info("Sending test messages...")
        
        # Test 1: Send simple numbers
        logger.info("\n--- Test 1: Sending speed values ---")
        for speed in [0, 25, 50, 65, 75, 85, 0]:
            msg = f"{speed}\n"
            ser.write(msg.encode('utf-8'))
            logger.info(f"Sent: {speed} MPH")
            time.sleep(0.1)
        
        # Test 2: Rapid updates (near real-time simulation)
        logger.info("\n--- Test 2: Rapid updates (real-time simulation) ---")
        import random
        for i in range(10):
            speed = random.randint(20, 80)
            msg = f"{speed}\n"
            ser.write(msg.encode('utf-8'))
            logger.info(f"Update {i+1}: {speed} MPH")
            time.sleep(0.05)  # 50ms = 20 updates/second
        
        # Test 3: Send a string message
        logger.info("\n--- Test 3: Sending text message ---")
        test_msg = "TEST\n"
        ser.write(test_msg.encode('utf-8'))
        logger.info("Sent: TEST")
        
        ser.close()
        logger.info("\n✓ Serial communication test complete!")
        logger.info("If you see this message, serial transmission was successful.")
        logger.info("Check your ESP32-S3 RGB666 TFT display to see if it received the data.")
        return True
        
    except serial.SerialException as e:
        logger.error(f"Serial error: {e}")
        logger.info("\nTroubleshooting:")
        logger.info("1. Make sure ESP32-S3 is connected via USB")
        logger.info("2. Check if another program is using the serial port")
        logger.info("3. Try unplugging and replugging the ESP32-S3")
        logger.info("4. On Linux, you may need to add your user to the dialout group:")
        logger.info("   sudo usermod -a -G dialout $USER")
        logger.info("   (then log out and back in)")
        return False
    except KeyboardInterrupt:
        logger.info("\nTest interrupted by user")
        if 'ser' in locals():
            ser.close()
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        if 'ser' in locals():
            ser.close()
        return False


def list_available_ports():
    """List all available serial ports"""
    logger.info("Available serial ports:")
    ports = serial.tools.list_ports.comports()
    if not ports:
        logger.info("  No serial ports found")
    for port in ports:
        vid_pid = ""
        if hasattr(port, 'vid') and hasattr(port, 'pid'):
            vid_pid = f" (VID:0x{port.vid:04X} PID:0x{port.pid:04X})"
        logger.info(f"  {port.device} - {port.description}{vid_pid}")


if __name__ == '__main__':
    print("=" * 60)
    print("ESP32-S3 Serial Communication Test")
    print("=" * 60)
    
    # List available ports
    list_available_ports()
    print()
    
    # Get port from command line or auto-detect
    port = None
    baudrate = 115200
    
    if len(sys.argv) > 1:
        port = sys.argv[1]
        logger.info(f"Using specified port: {port}")
    
    if len(sys.argv) > 2:
        try:
            baudrate = int(sys.argv[2])
            logger.info(f"Using specified baudrate: {baudrate}")
        except ValueError:
            logger.warning(f"Invalid baudrate '{sys.argv[2]}', using default 115200")
    
    # Run test
    success = test_serial_communication(port, baudrate)
    sys.exit(0 if success else 1)

