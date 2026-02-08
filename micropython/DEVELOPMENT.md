# MicroPython Development in Cursor

This guide explains how to develop MicroPython code for ESP32 directly in Cursor IDE.

## Setup

### 1. Install Required Tools

```bash
# Install ampy for file uploads (recommended)
pip3 install adafruit-ampy

# Install pyserial for serial communication
pip3 install pyserial

# Install Python development tools
pip3 install black flake8
```

### 2. Install Cursor/VS Code Extensions

The recommended extensions are listed in `.vscode/extensions.json`. Install them:

1. Open Cursor
2. Press `Cmd+Shift+P` (macOS) or `Ctrl+Shift+P` (Windows/Linux)
3. Type "Extensions: Show Recommended Extensions"
4. Install all recommended extensions

Or install manually:
- **Python** (ms-python.python)
- **Pylance** (ms-python.vscode-pylance)
- **Black Formatter** (ms-python.black-formatter)
- **Flake8** (ms-python.flake8)

### 3. Configure ESP32 Port

The upload script will auto-detect your ESP32 port, but you can also set it manually:

1. Find your ESP32 port:
   ```bash
   ls /dev/cu.*
   ```

2. Or use the task: `Cmd+Shift+P` → "Tasks: Run Task" → "Find ESP32 Port"

## Development Workflow

### Editing Code

1. **Open files in Cursor:**
   - All MicroPython files are in the `micropython/` directory
   - Edit them directly in Cursor with full syntax highlighting and IntelliSense

2. **Code Formatting:**
   - Files are automatically formatted on save (Black formatter)
   - Line length is set to 99 characters (MicroPython convention)

3. **Linting:**
   - Flake8 will show warnings/errors as you type
   - Note: Some MicroPython-specific code may show false warnings (e.g., `machine`, `network` modules)

### Uploading Code to ESP32

#### Step-by-step procedure (ampy)

The files to upload are: `wifi.dat`, `solar_flare_alert.py`, `wifi_manager.py`, `rainbow2.py`, and `boot.py`.

**Important:** Always upload `boot.py` **last**, because it may auto-start the program on import. Upload `wifi.dat` **first** so credentials are available.

##### If the board is running the old program (auto-start from boot.py)

1. **Stop the running program.** Connect via screen and press `Ctrl+C` (maybe several times) to get the `>>>` REPL prompt:
   ```bash
   screen /dev/cu.usbserial-0001 115200
   ```

2. **Wipe boot.py** so the board won't auto-start on next reboot:
   ```python
   f = open('boot.py', 'w'); f.write(''); f.close()
   ```

3. **Exit screen:** press `Ctrl+A`, then `K`, then `Y`.

4. **Upload all files** (boot.py last):
   ```bash
   cd micropython && ampy --port /dev/cu.usbserial-0001 put wifi.dat && ampy --port /dev/cu.usbserial-0001 put solar_flare_alert.py && ampy --port /dev/cu.usbserial-0001 put wifi_manager.py && ampy --port /dev/cu.usbserial-0001 put rainbow2.py && ampy --port /dev/cu.usbserial-0001 put boot.py
   ```

##### If the board is idle (no auto-start)

Just upload directly:
```bash
cd micropython && ampy --port /dev/cu.usbserial-0001 put wifi.dat && ampy --port /dev/cu.usbserial-0001 put solar_flare_alert.py && ampy --port /dev/cu.usbserial-0001 put wifi_manager.py && ampy --port /dev/cu.usbserial-0001 put rainbow2.py && ampy --port /dev/cu.usbserial-0001 put boot.py
```

##### Verify uploaded files

Connect via screen, then check file names and sizes:
```python
import os; [(f, os.stat(f)[6]) for f in os.listdir()]
```

Compare the sizes with your local files (`ls -la` in the `micropython/` directory).

##### Common upload issues

- **"could not enter raw repl"**: The serial port is in use. Close any `screen` session or kill processes using the port:
  ```bash
  lsof | grep "cu.usbserial" | awk '{print $2}' | xargs kill
  ```
- **Port not found**: Check the port name with `ls /dev/cu.*`
- **Timeout**: Press the reset button on the board and try again immediately

### Testing Code

#### Serial Monitor (REPL)

Connect to the ESP32 REPL using screen in the Cursor terminal:
```bash
screen /dev/cu.usbserial-0001 115200
# Press Ctrl+A then K, then Y to exit
```

#### Interactive Testing

Connect to ESP32 via screen and test functions interactively:

```python
import solar_flare_alert

# Test WiFi
from wifi_manager import WifiManager
wm = WifiManager()
wm.connect()

# Test GOES data
val = solar_flare_alert.get_current_goes_val()
print(val)

# Test LED
import machine
led = machine.PWM(machine.Pin(27), freq=500, duty=512)
led.duty(1023)  # Full brightness
```

## Project Structure

```
micropython/
├── boot.py                 # Auto-runs on ESP32 boot
├── solar_flare_alert.py   # Main program
├── wifi_manager.py        # WiFi connection manager
├── rainbow2.py           # Color table for LED strip mode
├── upload_to_esp32.py    # Upload script
├── DEVELOPMENT.md        # This file
└── SETUP_ESP32.md        # Initial setup guide
```

## Code Style

- **Indentation:** 4 spaces
- **Line length:** 99 characters (MicroPython convention)
- **Formatting:** Black formatter (auto-format on save)
- **Linting:** Flake8

## Tips & Best Practices

### 1. Development Mode

Set `RUN = False` in `solar_flare_alert.py` to prevent the main loop from running, allowing interactive testing:

```python
RUN = False  # Set to False for testing
```

### 2. Debug Output

Enable debug mode for verbose output:

```python
DEBUG = True  # More verbose output
```

### 3. File Organization

- Keep all MicroPython files in the `micropython/` directory
- Files are uploaded to the root of the ESP32 filesystem
- Don't create subdirectories on ESP32 (MicroPython limitation)

### 4. Testing Workflow

1. Edit code in Cursor
2. Save file (auto-formatted)
3. Upload to ESP32 using task or script
4. Reset ESP32 or use serial monitor to test
5. Iterate

### 5. Common Issues

**Import errors:**
- Make sure all files are uploaded
- Check file names match exactly (case-sensitive)
- Files must be in ESP32 root directory

**Upload fails:**
- Check ESP32 is connected and port is correct
- Try resetting ESP32 before upload
- Make sure no other program is using the serial port (close any `screen` sessions)

**Code not running:**
- Check `boot.py` imports `solar_flare_alert`
- Verify `RUN = True` in `solar_flare_alert.py`
- Check serial monitor for error messages

## Keyboard Shortcuts

- `Cmd+S` (macOS) / `Ctrl+S` (Windows/Linux): Save and format
- `Cmd+Shift+P`: Command palette
- `Cmd+Shift+B`: Run build task (if configured)
- `Cmd+\``: Toggle terminal

## Advanced: Custom Tasks

You can add custom tasks in `.vscode/tasks.json`. For example:

```json
{
  "label": "Upload and Monitor",
  "type": "shell",
  "command": "${workspaceFolder}/micropython/upload_to_esp32.py && screen ${input:esp32Port} 115200",
  "dependsOn": "Upload to ESP32"
}
```

## Resources

- [MicroPython ESP32 Documentation](https://docs.micropython.org/en/latest/esp32/quickref.html)
- [Adafruit ampy Documentation](https://github.com/adafruit/ampy)
- [VS Code Python Extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python)

