# Troubleshooting Guide

## OSError: error 30 read-only filesystem

This error occurs when trying to write to a read-only filesystem. Here are common causes and solutions:

### On ESP32-S3 / MicroPython

**Problem:** ESP32-S3 filesystem is read-only or corrupted.

**Solutions:**

1. **Remount filesystem as read-write (if possible):**
   ```python
   import os
   os.mount('/', '/', readonly=False)
   ```

2. **Check filesystem status:**
   ```python
   import os
   stat = os.statvfs('/')
   print(f"Free space: {stat[0] * stat[3]} bytes")
   ```

3. **Re-flash the filesystem:**
   - Use `mpremote` or `ampy` to erase and re-flash the filesystem
   - Or use the ESP32 flash tool to reformat the partition

4. **Use RAM for temporary files:**
   - Instead of writing to filesystem, use in-memory variables
   - The code should not need to write files for normal operation

### On Raspberry Pi

**Problem:** Filesystem mounted read-only (often after improper shutdown).

**Solutions:**

1. **Check filesystem status:**
   ```bash
   mount | grep " / "
   # Should show rw (read-write), not ro (read-only)
   ```

2. **Remount as read-write:**
   ```bash
   sudo mount -o remount,rw /
   ```

3. **Check for filesystem errors:**
   ```bash
   sudo fsck -f /dev/mmcblk0p2  # Adjust partition as needed
   ```

4. **If framebuffer access fails:**
   - The framebuffer device might be read-only
   - Try running with sudo: `sudo python main.py`
   - Or add user to video group: `sudo usermod -a -G video $USER`

### In the Code

**If error occurs in display.py framebuffer access:**

The framebuffer device (`/dev/fb1`) might be read-only. The code already handles this gracefully by falling back to simulation mode, but you can:

1. **Check framebuffer permissions:**
   ```bash
   ls -l /dev/fb*
   ```

2. **Fix permissions (if needed):**
   ```bash
   sudo chmod 666 /dev/fb1
   ```

3. **Add user to video group:**
   ```bash
   sudo usermod -a -G video $USER
   # Log out and back in
   ```

### For Systemd Service

If running as a service, make sure:

1. **Service has proper permissions:**
   - Check the `User=` directive in the service file
   - User should have access to serial ports and display devices

2. **Check service logs:**
   ```bash
   sudo journalctl -u hudler.service -n 50
   ```

3. **Test manually first:**
   ```bash
   # Run as the service user to test
   sudo -u raspberry python /home/raspberry/code/hudler/main.py
   ```

## Common Solutions Summary

1. **ESP32-S3:** Re-flash filesystem or use RAM-only operations
2. **Raspberry Pi:** Remount filesystem as read-write
3. **Framebuffer:** Check permissions, add user to video group
4. **Service:** Verify user permissions in systemd service file

