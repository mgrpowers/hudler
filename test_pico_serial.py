#!/usr/bin/env python3
"""
Test script for Mac/Raspberry Pi → Pico/ESP32-S3 serial communication
Tests near real-time message sending over USB serial to:
- Raspberry Pi Pico (with Pico Scroll Pack)
- Qualia ESP32-S3 RGB666 TFT Display

Auto-detects connected device or specify device type with --device flag
"""

import serial
import serial.tools.list_ports
import time
import logging
import sys
import argparse

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


def find_esp32_port():
    """Find the serial port for ESP32-S3"""
    ports = serial.tools.list_ports.comports()
    
    # Common identifiers for ESP32-S3
    esp32_identifiers = ['ESP32', 'ESP32-S3', 'CH340', 'CP210', 'Silicon Labs', 'USB Serial', 'Qualia']
    
    for port in ports:
        logger.info(f"Found port: {port.device} - {port.description}")
        # Check if it looks like an ESP32
        if any(identifier in port.description for identifier in esp32_identifiers):
            logger.info(f"Potential ESP32-S3 found: {port.device}")
            return port.device
        
        # Also check VID/PID if available
        # CH340: 0x1A86, CP210x: 0x10C4, ESP32-S3: 0x303A, Adafruit: 0x239A
        if hasattr(port, 'vid') and hasattr(port, 'pid'):
            if port.vid in [0x1A86, 0x10C4, 0x303A, 0x239A]:  # Common ESP32 USB-to-Serial chips
                logger.info(f"ESP32-S3 found by VID: {port.device}")
                return port.device
    
    return None


def find_device_port(device_type='auto'):
    """Find serial port for specified device type"""
    if device_type == 'pico':
        return find_pico_port(), 'Pico'
    elif device_type == 'esp32' or device_type == 'qualia':
        return find_esp32_port(), 'ESP32-S3'
    else:  # auto-detect
        # Try ESP32 first (more specific identifiers)
        esp32_port = find_esp32_port()
        if esp32_port:
            return esp32_port, 'ESP32-S3'
        
        # Then try Pico
        pico_port = find_pico_port()
        if pico_port:
            return pico_port, 'Pico'
        
        return None, None


def test_serial_communication(port_name=None, device_type='auto', baudrate=115200, 
                               continuous=False, interval=0.1, max_speed=100):
    """Test sending messages to Pico or ESP32-S3 over serial
    
    Args:
        port_name: Serial port path (None for auto-detect)
        device_type: Device type ('auto', 'pico', 'esp32')
        baudrate: Serial baudrate (default: 115200)
        continuous: If True, run continuously sending speed values
        interval: Time between messages in seconds (default: 0.1 = 100ms)
        max_speed: Maximum speed value for continuous mode (default: 100 MPH)
    """
    
    device_name = None
    if port_name is None:
        port_name, device_name = find_device_port(device_type)
    
    if port_name is None:
        logger.error("No device serial port found!")
        logger.info(f"\nPlease connect your device and try again.")
        logger.info("Or specify the port manually: python test_pico_serial.py /dev/tty.usbmodemXXX")
        logger.info("Or specify device type: python test_pico_serial.py --device pico|esp32")
        return False
    
    if device_name is None:
        device_name = "Device"  # Fallback
    
    try:
        logger.info(f"Opening serial connection to {device_name} on {port_name} at {baudrate} baud...")
        ser = serial.Serial(port_name, baudrate, timeout=1)
        time.sleep(2)  # Give device time to initialize
        
        logger.info(f"Serial connection established to {device_name}!")
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
        if not continuous:
            logger.info("\n--- Test 3: Sending text message ---")
            test_msg = "TEST\n"
            ser.write(test_msg.encode('utf-8'))
            logger.info("Sent: TEST")
            
            ser.close()
            logger.info(f"\n✓ Serial communication test complete!")
            logger.info("If you see this message, serial transmission was successful.")
            logger.info(f"Check your {device_name} display to see if it received the data.")
            return True
        
        # Continuous mode: Send speed values at specified interval
        logger.info(f"\n--- Continuous Mode: Sending speed values every {interval*1000:.0f}ms ---")
        logger.info("Press Ctrl+C to stop")
        logger.info(f"Speed range: 0-{max_speed} MPH\n")
        
        import random
        
        count = 0
        speed = 0
        direction = 1  # 1 for increasing, -1 for decreasing
        
        try:
            while True:
                # Generate speed value (simulate gradual acceleration/deceleration)
                if random.random() < 0.7:  # 70% chance to continue in same direction
                    speed += direction * random.randint(1, 5)
                    if speed <= 0:
                        speed = 0
                        direction = 1
                    elif speed >= max_speed:
                        speed = max_speed
                        direction = -1
                else:
                    # 30% chance to change direction or jump
                    speed = random.randint(0, max_speed)
                
                # Send speed
                msg = f"{int(speed)}\n"
                ser.write(msg.encode('utf-8'))
                count += 1
                
                # Log every 10th message to reduce spam
                if count % 10 == 0:
                    logger.info(f"Sent {count} messages | Current speed: {int(speed)} MPH")
                
                time.sleep(interval)
        
        except KeyboardInterrupt:
            logger.info("\n\nStopping continuous mode...")
        
        ser.close()
        logger.info(f"\n✓ Continuous mode stopped")
        logger.info(f"Total messages sent: {count}")
        logger.info(f"Final speed: {int(speed)} MPH")
        return True
        
    except serial.SerialException as e:
        logger.error(f"Serial error: {e}")
        logger.info(f"\nTroubleshooting:")
        logger.info(f"1. Make sure {device_name} is connected via USB")
        logger.info("2. Check if another program is using the serial port")
        logger.info(f"3. Try unplugging and replugging the {device_name}")
        if device_name == 'ESP32-S3':
            logger.info("4. On Linux, you may need to add your user to the dialout group:")
            logger.info("   sudo usermod -a -G dialout $USER")
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
    parser = argparse.ArgumentParser(
        description='Test serial communication with Pico Scroll or Qualia ESP32-S3',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto-detect device
  python test_pico_serial.py
  
  # Specify port
  python test_pico_serial.py /dev/tty.usbmodemXXX
  
  # Specify device type (auto-detect port)
  python test_pico_serial.py --device pico
  python test_pico_serial.py --device esp32
  
  # Continuous mode (100ms interval)
  python test_pico_serial.py --continuous
  
  # Continuous mode with custom interval (50ms = 0.05s)
  python test_pico_serial.py --continuous --interval 0.05
  
  # Continuous mode with max speed
  python test_pico_serial.py --continuous --max-speed 80
        """
    )
    parser.add_argument('port', nargs='?', help='Serial port (e.g., /dev/tty.usbmodemXXX)')
    parser.add_argument('baudrate', nargs='?', type=int, default=115200, help='Baudrate (default: 115200)')
    parser.add_argument('--device', choices=['pico', 'esp32', 'qualia', 'auto'], default='auto',
                       help='Device type to detect (default: auto-detect)')
    parser.add_argument('--continuous', '-c', action='store_true',
                       help='Run continuously, sending speed values at specified interval')
    parser.add_argument('--interval', '-i', type=float, default=0.1,
                       help='Interval between messages in seconds (default: 0.1 = 100ms)')
    parser.add_argument('--max-speed', '-m', type=int, default=100,
                       help='Maximum speed value for continuous mode (default: 100 MPH)')
    
    args = parser.parse_args()
    
    print("=" * 60)
    if args.continuous:
        print("Pico/ESP32-S3 Serial Communication Test - CONTINUOUS MODE")
    else:
        print("Pico/ESP32-S3 Serial Communication Test")
    print("=" * 60)
    
    # List available ports
    list_available_ports()
    print()
    
    # Run test
    success = test_serial_communication(
        args.port, 
        args.device, 
        args.baudrate,
        args.continuous,
        args.interval,
        args.max_speed
    )
    sys.exit(0 if success else 1)


