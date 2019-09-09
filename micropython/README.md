# MicroPython port to run on ESPs

## Flashing MicroPython to ESP32 D1 Mini

Board available at https://www.bastelgarage.ch/esp8266-esp32/esp32minikit-wemos or at your far Eastern supplier for around 6 bucks.

1. Install `esptool` either using `pip install esptool` or trough your packagemanager on Linux
2. Download the recent firmware from http://micropython.org/download#esp32
3. From the folder were you downloaded the firmware run `esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash` to erase the flash
4. Run `esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 <DOWNLOADED_FIRMWARE>.bin` to flash it.
5. Open a serial terminal (screen, putty, picocom) to check if you get a python shell.

### ESP32 MicroPython tutorial:
https://docs.micropython.org/en/latest/esp32/quickref.html


## Installing Thonny

Thonny is a simple IDE for Python, MicroPython and CircuitPython (Adafruits MicroPython fork), it allows to upload your programs to a MicroPython board easily, also when it doesn't show up as a USB drive.

To install it, the go to https://thonny.org/

### Thonny tutorial
https://randomnerdtutorials.com/getting-started-thonny-micropython-python-ide-esp32-esp8266/

## Upload code
Open `main.py` in Thonny, change the WiFi credentials to your network, check if the LED pins are correct, the pinnames on ESPs are a bit weird from time to time.

## Wiring
On my board the pins are labled with **IOxx** so it was pretty straight forward. The pins deliver 3.3V and some sources say max 12mA, I took 330 Ohm, for 10mA.

## Testing
In line 11 set RUN to False, the program loop wont run and you can test the functions. For example if the LEDs light up correctly.
