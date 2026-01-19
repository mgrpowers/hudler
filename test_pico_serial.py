#!/usr/bin/env python3
"""
Test script for Mac → Pico serial communication
Tests near real-time message sending over USB serial to Raspberry Pi Pico
"""

import serial
import serial.tools.list_ports
import time
import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def find_pico_port():
    """Find the serial port for Raspberry Pi Pico"""
    ports = serial.tools.list_ports.comports()
    
    # Common identifiers for Raspberry Pi Pico
    pico_identifiers = ['Pico', 'pico', 'Raspberry Pi Pico', 'RPI', 'Serial', 'USB Serial']
    
    for port in ports:
        logger.info(f"Found port: {port.device} - {port.description}")
        # Check if it looks like a Pico
        if any(identifier in port.description for identifier in pico_identifiers):
            logger.info(f"Potential Pico found: {port.device}")
            return port.device
        
        # Also check VID/PID if available (Pico uses: 2E8A:0005 or similar)
        if hasattr(port, 'vid') and hasattr(port, 'pid'):
            if port.vid == 0x2E8A:  # Raspberry Pi Foundation VID
                logger.info(f"Pico found by VID: {port.device}")
                return port.device
    
    return None


def test_serial_communication(port_name=None, baudrate=115200):
    """Test sending messages to Pico over serial"""
    
    if port_name is None:
        port_name = find_pico_port()
    
    if port_name is None:
        logger.error("No Pico serial port found!")
        logger.info("\nPlease connect your Pico and try again.")
        logger.info("Or specify the port manually: python test_pico_serial.py /dev/tty.usbmodemXXX")
        return False
    
    try:
        logger.info(f"Opening serial connection to {port_name} at {baudrate} baud...")
        ser = serial.Serial(port_name, baudrate, timeout=1)
        time.sleep(2)  # Give Pico time to initialize
        
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
        logger.info("Check your Pico display to see if it received the data.")
        return True
        
    except serial.SerialException as e:
        logger.error(f"Serial error: {e}")
        logger.info("\nTroubleshooting:")
        logger.info("1. Make sure Pico is connected via USB")
        logger.info("2. Check if another program is using the serial port")
        logger.info("3. Try unplugging and replugging the Pico")
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
        logger.info(f"  {port.device} - {port.description}")


if __name__ == '__main__':
    print("=" * 60)
    print("Pico Serial Communication Test")
    print("=" * 60)
    
    # List available ports
    list_available_ports()
    print()
    
    # Get port from command line or auto-detect
    port = None
    if len(sys.argv) > 1:
        port = sys.argv[1]
        logger.info(f"Using specified port: {port}")
    
    # Run test
    success = test_serial_communication(port)
    sys.exit(0 if success else 1)

