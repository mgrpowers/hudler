# Pico Scroll Display Debugging Guide

## Issue: Data is being sent but nothing appears on the display

If your test script shows successful transmission but the Pico Scroll isn't displaying anything, check these items:

## Checklist

### 1. Is the Pico Code Running?

**Most Common Issue:** The code must be saved as `main.py` on the Pico to run automatically.

- [ ] Open Thonny (or your MicroPython IDE)
- [ ] Connect to your Pico
- [ ] Upload `pico_scroll_example.py` as `main.py` to the Pico
- [ ] Check the REPL console for "Waiting for speed data..." message
- [ ] If you see output in the console, the code is running

**Test:** Disconnect and reconnect the Pico. The code should run automatically if it's named `main.py`.

### 2. Is Pimoroni MicroPython Firmware Installed?

The Pico Scroll requires Pimoroni's custom MicroPython firmware.

- [ ] Download from: https://github.com/pimoroni/pimoroni-pico/releases
- [ ] Flash the `.uf2` file to your Pico (hold BOOTSEL while plugging in USB)
- [ ] After flashing, the Pico will reboot

**Verify:** In Thonny REPL, try:
```python
from picoscroll import PicoScroll
```
If this doesn't work, you need the Pimoroni firmware.

### 3. Is Serial Data Being Received?

Use the debug version to see if data is arriving:

- [ ] Upload `pico_scroll_debug.py` as `main.py` to your Pico
- [ ] Run your test script: `python test_pico_serial.py`
- [ ] Watch the Thonny REPL console for `[X] Received: 'XX'` messages
- [ ] If you see these messages, serial communication is working!

### 4. Display Hardware Check

Verify the display hardware is working:

**In Thonny REPL, try:**
```python
from picoscroll import PicoScroll
scroll = PicoScroll()
scroll.clear()
scroll.write_text("TEST", 0, 0)
scroll.update()
```

You should see "TEST" on the display. If not:
- [ ] Check physical connections between Pico and Scroll Pack
- [ ] Verify the Scroll Pack is powered (power LED should be on)
- [ ] Check for loose connections

### 5. API Differences

The Pico Scroll API may differ between firmware versions. Try these in Thonny REPL:

```python
from picoscroll import PicoScroll
scroll = PicoScroll()

# Try different methods:
scroll.write_text("TEST", 0, 0)
scroll.update()

# Or:
scroll.text("TEST", 0, 0, 0, 7)
scroll.update()

# Or:
scroll.set_text("TEST")
scroll.update()
```

One of these should work. Update the code with the working method.

## Quick Diagnostic Steps

1. **Check if code is running:**
   - Upload `pico_scroll_example.py` as `main.py`
   - Look for "Waiting for speed data..." in console

2. **Check if serial data arrives:**
   - Run `python test_pico_serial.py` from your Mac
   - Check Thonny console for received messages

3. **Check if display works:**
   - Test with simple REPL commands (see #4 above)

4. **Check API compatibility:**
   - Try different display methods (see #5 above)

## Common Solutions

**Problem:** No messages in console
- **Solution:** Code not running - make sure it's named `main.py`

**Problem:** Console shows messages but no display
- **Solution:** Display API issue - try different methods (see #5)

**Problem:** "picoscroll not available" error
- **Solution:** Need Pimoroni MicroPython firmware

**Problem:** Serial port not found
- **Solution:** Check USB connection, try different port in test script

