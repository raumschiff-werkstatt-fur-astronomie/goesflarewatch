# ESP32 MicroPython Setup Guide

This guide will help you set up MicroPython on your ESP32 dev board and upload the Solar Flare Alert code.

## Prerequisites

### 1. Install esptool (for flashing MicroPython)

On macOS, you can install esptool using pip or brew:

```bash
# Using pip (if you have Python installed)
pip3 install esptool

# OR using brew
brew install esptool
```

### 2. Install ampy (for uploading files)

```bash
pip3 install adafruit-ampy
```

## Step 1: Flash MicroPython to ESP32

### Find your ESP32 port

On macOS, the port is usually something like:
- `/dev/cu.usbserial-0001` (M1 Macs)
- `/dev/cu.usbmodem*` or `/dev/cu.SLAB_USBtoUART*`

You can find it by:
1. Plugging in your ESP32
2. Running: `ls /dev/cu.*` in the Cursor terminal

### Download MicroPython firmware

1. Go to: http://micropython.org/download#esp32
2. Download the latest stable ESP32 firmware (`.bin` file)

### Flash the firmware

```bash
# Replace /dev/cu.usbserial-0001 with your actual port
# Replace esp32-xxxxx.bin with your downloaded firmware file

# First, erase the flash
esptool.py --chip esp32 --port /dev/cu.usbserial-0001 erase_flash

# Then flash MicroPython
esptool.py --chip esp32 --port /dev/cu.usbserial-0001 --baud 460800 write_flash -z 0x1000 esp32-xxxxx.bin
```

**Note:** If you get permission errors, you may need to use `sudo` or add your user to the dialout group.

## Step 2: Upload Code Files

### Using ampy from the Cursor terminal

Upload files in this order (`wifi.dat` first, `boot.py` last):

```bash
cd micropython && ampy --port /dev/cu.usbserial-0001 put wifi.dat && ampy --port /dev/cu.usbserial-0001 put solar_flare_alert.py && ampy --port /dev/cu.usbserial-0001 put wifi_manager.py && ampy --port /dev/cu.usbserial-0001 put rainbow2.py && ampy --port /dev/cu.usbserial-0001 put boot.py
```

**Note:** If the board is running the old program, you need to stop it first. See `DEVELOPMENT.md` for detailed instructions.

### Verify files are uploaded

Connect to the REPL and check file names and sizes:
```bash
screen /dev/cu.usbserial-0001 115200
```
```python
import os; [(f, os.stat(f)[6]) for f in os.listdir()]
```
Exit screen: `Ctrl+A`, then `K`, then `Y`.

## Step 3: Configure Your Setup

### Edit `solar_flare_alert.py` configuration

Open `solar_flare_alert.py` in Cursor and check these settings:

**LED Configuration:**
```python
SINGLE_LED_MODE = True   # Set to True for single LED
LED_STRIP_MODE = False   # Set to True for RGB LED strip

# LED pin numbers (adjust for your board)
if SINGLE_LED_MODE:
    LEDS = [27]  # Change 27 to your LED pin
elif LED_STRIP_MODE:
    LEDS = [13, 12, 27]  # R, G, B pins
```

**Status LED:**
```python
STATUS_LED = 2  # Usually the built-in LED on ESP32
# For ESP32-D boards without built-in LED, set to None:
# STATUS_LED = None
# NOTE: Do NOT use the same pin as your signal LED - use a different unused pin or None
```

**Debug mode:**
```python
DEBUG = True   # Set to True for verbose output
RUN = True     # Set to False to stop the main loop for testing
```

### Hardware Wiring

- **Single LED mode**: Connect LED with 110Ω resistor to GPIO pin 27 (or your chosen pin)
- **LED Strip mode**: Connect RGB channels to GPIO pins 13, 12, 27 (R, G, B)
- **Status LED**: Usually built-in on pin 2 (ESP32-D boards may not have one - set `STATUS_LED = None` in code)

**Important:** ESP32 pins output 3.3V with max ~12mA. Use appropriate resistors!

## Step 4: First Run

1. **Reset your ESP32** (press the reset button or unplug/replug USB)

2. **Watch the serial output** via screen. You should see:
   - "I am alive!"
   - WiFi connection attempts
   - GOES data fetching

3. **WiFi Setup:**
   - On first run, if no WiFi credentials are saved, the ESP32 will create an access point
   - Connect to the WiFi network "WifiManager" (password: "wifimanager")
   - Open a browser and go to the IP shown (usually 192.168.4.1)
   - Select your WiFi network and enter the password
   - The device will save credentials and reboot

## Step 5: Testing

### Test LED without running main loop

1. In `solar_flare_alert.py`, set `RUN = False`
2. Upload the file
3. Reset ESP32
4. In the REPL (via `screen`), test manually:
```python
import machine
led = machine.PWM(machine.Pin(27), freq=500, duty=512)
led.duty(1023)  # Full brightness
led.duty(0)     # Off
```

### Test WiFi connection

```python
from wifi_manager import WifiManager
wm = WifiManager()
wm.connect()
wm.is_connected()
wm.get_address()
```

### Test GOES data fetching

```python
import solar_flare_alert
val = solar_flare_alert.get_current_goes_val()
print(val)
```

## Troubleshooting

### ESP32 not detected
- Try a different USB cable (data cable, not just charging)
- Check if drivers are needed (some ESP32 boards need CH340 or CP2102 drivers)
- On macOS, you might need to allow the USB device in System Preferences → Security

### Permission denied errors
```bash
sudo chmod 666 /dev/cu.usbserial-0001
```

### Import errors
- Make sure all files are uploaded to the ESP32
- Check that filenames match exactly (case-sensitive)
- Files should be in the root directory, not in subfolders

### WiFi connection issues
- Make sure your WiFi network is 2.4GHz (ESP32 doesn't support 5GHz)
- Check that the password is correct
- Try deleting `wifi.dat` file and reconfiguring

### LED not working
- Check wiring and resistor values
- Verify GPIO pin numbers match your board
- Test with a simple blink program first
- Make sure the LED polarity is correct (anode/cathode)

## Additional Resources

- MicroPython ESP32 docs: https://docs.micropython.org/en/latest/esp32/quickref.html
- Project documentation: https://solar-flare-alert.readthedocs.io/
- Adafruit ampy: https://github.com/adafruit/ampy

## Quick Reference Commands

```bash
# List serial ports
ls /dev/cu.*

# Flash MicroPython
esptool.py --chip esp32 --port /dev/cu.usbserial-0001 erase_flash
esptool.py --chip esp32 --port /dev/cu.usbserial-0001 --baud 460800 write_flash -z 0x1000 firmware.bin

# Access serial console (REPL)
screen /dev/cu.usbserial-0001 115200
# Press Ctrl+A then K then Y to exit
```

