#!/usr/bin/env python3
"""
Manual file upload via REPL - use this if ampy doesn't work.
Run this script, then copy-paste the output into your REPL.
"""
import sys

file_path = "micropython/solar_flare_alert.py"

print("=" * 60)
print("Copy and paste the following into your MicroPython REPL:")
print("=" * 60)
print()

with open(file_path, 'r') as f:
    content = f.read()

# Create file and write content
print("f = open('solar_flare_alert.py', 'w')")
print()

for line in content.split('\n'):
    # Escape quotes and backslashes
    escaped = line.replace('\\', '\\\\').replace("'", "\\'")
    print(f"f.write('{escaped}\\n')")

print()
print("f.close()")
print()
print("=" * 60)
print("After pasting, the file will be uploaded.")
print("Then reset the ESP32 or run: import solar_flare_alert")
