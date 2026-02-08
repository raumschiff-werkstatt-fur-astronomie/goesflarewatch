#!/usr/bin/env python3
"""
Upload MicroPython files to ESP32 using ampy or direct serial connection.

This script can upload individual files or all files in the micropython directory.

Usage:
    python upload_to_esp32.py [file1] [file2] ...
    python upload_to_esp32.py  # Uploads all .py files in micropython directory
"""

import sys
import os
import glob
import time
import serial
import serial.tools.list_ports
from pathlib import Path

# Try to import ampy (preferred method)
try:
    from ampy import pyboard
    from ampy.files import Files
    AMPY_AVAILABLE = True
except ImportError:
    AMPY_AVAILABLE = False
    print("Warning: ampy not installed. Install with: pip3 install adafruit-ampy")
    print("Falling back to basic serial upload...")

# Configuration
MICROPYTHON_DIR = Path(__file__).parent
BAUD_RATE = 115200
TIMEOUT = 5

# Files to upload (in order)
DEFAULT_FILES = [
    "wifi_manager.py",
    "rainbow2.py",
    "solar_flare_alert.py",
    "boot.py"
]


def find_esp32_port():
    """Find the ESP32 serial port automatically."""
    ports = serial.tools.list_ports.comports()
    
    # Common ESP32 USB-to-Serial chip identifiers
    esp32_identifiers = [
        "CP210",  # Silicon Labs CP210x
        "CH340",  # WCH CH340
        "FTDI",   # FTDI FT232
        "USB Serial",  # Generic
        "USB2.0-Serial"  # Generic
    ]
    
    for port in ports:
        description = port.description.upper()
        for identifier in esp32_identifiers:
            if identifier.upper() in description:
                return port.device
    
    # Fallback: look for common macOS port patterns
    import glob
    mac_ports = glob.glob("/dev/cu.usbserial*") + glob.glob("/dev/cu.SLAB*")
    if mac_ports:
        return mac_ports[0]
    
    return None


def upload_with_ampy(port, file_path):
    """Upload file using ampy (preferred method)."""
    try:
        board = pyboard.Pyboard(port, baudrate=BAUD_RATE)
        files = Files(board)
        
        filename = os.path.basename(file_path)
        print(f"Uploading {filename} to ESP32...")
        
        with open(file_path, 'rb') as f:
            content = f.read()
        
        files.put(filename, content)
        print(f"✓ {filename} uploaded successfully")
        
        board.close()
        return True
    except Exception as e:
        print(f"✗ Error uploading {file_path}: {e}")
        return False


def upload_with_serial(port, file_path):
    """Upload file using direct serial connection (fallback)."""
    try:
        ser = serial.Serial(port, BAUD_RATE, timeout=TIMEOUT)
        
        # Wait for MicroPython prompt
        ser.write(b'\r\n')
        time.sleep(0.5)
        ser.read(100)  # Clear buffer
        
        filename = os.path.basename(file_path)
        print(f"Uploading {filename} to ESP32 via serial...")
        
        # Read file content
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Enter file editing mode
        ser.write(b'f = open(\'{}\', \'w\')\r\n'.format(filename.encode()))
        time.sleep(0.1)
        
        # Write file line by line
        for line in content.split('\n'):
            # Escape quotes and special characters
            escaped_line = line.replace('\\', '\\\\').replace("'", "\\'")
            ser.write(f"f.write('{escaped_line}\\n')\r\n".encode())
            time.sleep(0.05)
        
        # Close file
        ser.write(b'f.close()\r\n')
        time.sleep(0.1)
        
        ser.close()
        print(f"✓ {filename} uploaded successfully")
        return True
    except Exception as e:
        print(f"✗ Error uploading {file_path}: {e}")
        return False


def main():
    """Main upload function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Upload MicroPython files to ESP32')
    parser.add_argument('files', nargs='*', help='Files to upload (default: all .py files)')
    parser.add_argument('--port', '-p', help='Serial port (auto-detected if not specified)')
    parser.add_argument('--list-ports', action='store_true', help='List available serial ports')
    
    args = parser.parse_args()
    
    # List ports if requested
    if args.list_ports:
        print("Available serial ports:")
        ports = serial.tools.list_ports.comports()
        for port in ports:
            print(f"  {port.device} - {port.description}")
        return
    
    # Find ESP32 port
    if args.port:
        port = args.port
    else:
        port = find_esp32_port()
        if not port:
            print("Error: Could not find ESP32 port automatically.")
            print("Please specify with --port or use --list-ports to see available ports")
            return
        print(f"Using port: {port}")
    
    # Determine files to upload
    if args.files:
        files_to_upload = [Path(f) for f in args.files]
    else:
        # Upload all .py files in micropython directory
        files_to_upload = []
        for filename in DEFAULT_FILES:
            file_path = MICROPYTHON_DIR / filename
            if file_path.exists():
                files_to_upload.append(file_path)
            else:
                print(f"Warning: {filename} not found, skipping...")
    
    if not files_to_upload:
        print("No files to upload!")
        return
    
    # Upload files
    print(f"\nUploading {len(files_to_upload)} file(s) to ESP32...\n")
    
    success_count = 0
    for file_path in files_to_upload:
        if not file_path.exists():
            print(f"✗ {file_path} not found, skipping...")
            continue
        
        if AMPY_AVAILABLE:
            success = upload_with_ampy(port, file_path)
        else:
            success = upload_with_serial(port, file_path)
        
        if success:
            success_count += 1
    
    print(f"\n✓ Upload complete: {success_count}/{len(files_to_upload)} files uploaded successfully")
    
    if success_count == len(files_to_upload):
        print("\nYou can now reset your ESP32 to run the code.")


if __name__ == "__main__":
    main()

