How to use the solar flare alert on micropython
===============================================

Flashing MicroPython to ESP32
-----------------------------

The board is a development kit and is
available at many places, e.g.
https://www.bastelgarage.ch/nodemcu-32s-esp32-wifi-bluetooth-entwicklungs-board?search=wroom
and you should find easily one near you.

* Install ``esptool`` either using ``pip install esptool`` or trough your package manager on Linux
* Download the recent firmware from http://micropython.org/download#esp32
* From the folder were you downloaded the firmware run ``esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash`` to erase the flash
* Run ``esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 <DOWNLOADED_FIRMWARE>.bin`` to flash it.
* Open a serial terminal (screen, putty, picocom) to check if you get a python shell.

ESP32 MicroPython tutorial
^^^^^^^^^^^^^^^^^^^^^^^^^^^
See https://docs.micropython.org/en/latest/esp32/quickref.html

Installing Thonny
-----------------

Thonny is a simple IDE for Python,
MicroPython and CircuitPython (Adafruits MicroPython fork),
it allows to upload your programs to a MicroPython board easily,
also when it doesn't show up as a USB drive.

To install it, the go to https://thonny.org/

Thonny tutorial
^^^^^^^^^^^^^^^

See https://randomnerdtutorials.com/getting-started-thonny-micropython-python-ide-esp32-esp8266/

Upload code
===========

Open `solar_flare_alert.py` in Thonny,
check if the LED pins are correct,
the pin names on ESPs are a bit weird from time to time.

In the file boot.py, which should already be on the board, change the line
`import main` to `import solar_flare_alert`

Wiring
======
On our board the pins are labeled with **IOxx** so it is
pretty straight forward.
The pins deliver 3.3V and some sources say max 12mA, we use a 110 Ohm resistor.

Testing
=======
In line 11 set RUN to False,
the program loop wont run and you can test the functions.
For example if the LED lights up correctly.
