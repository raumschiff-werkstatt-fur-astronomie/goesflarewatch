How to install the solar flare alert software on the ESP32 board
===================================================================

Prerequisites
-------------

Install the required tools on your computer:

.. code-block:: bash

   pip3 install esptool adafruit-ampy pyserial

Flashing MicroPython to ESP32
-----------------------------

The ESP32 development board is available at
various places, such as `Bastelgarage <https://www.bastelgarage.ch/nodemcu-32s-esp32-wifi-bluetooth-entwicklungs-board?search=wroom>`_, where you can easily find one near you.

* Download the recent firmware from http://micropython.org/download#esp32
* Find your ESP32 port by running ``ls /dev/cu.*`` in the terminal
* Erase the flash: ``esptool.py --chip esp32 --port /dev/cu.usbserial-0001 erase_flash``
* Flash the firmware: ``esptool.py --chip esp32 --port /dev/cu.usbserial-0001 --baud 460800 write_flash -z 0x1000 <DOWNLOADED_FIRMWARE>.bin``
* Open a serial terminal to check if you get a Python shell: ``screen /dev/cu.usbserial-0001 115200``

On Mac, the port is typically ``/dev/cu.usbserial-0001`` (M1/Apple Silicon) or
``/dev/cu.SLAB_USBtoUART`` (older Macs). If you don't see the device, try a
different USB cable (must be a data cable, not just charging).

ESP32 MicroPython tutorial
^^^^^^^^^^^^^^^^^^^^^^^^^^^
See https://docs.micropython.org/en/latest/esp32/quickref.html

Upload code
===========

All the code for this project is on GitHub in the ``micropython/`` directory.

The following files need to be uploaded to the ESP32:

* ``wifi.dat`` -- WiFi credentials (upload first)
* ``solar_flare_alert.py`` -- main program
* ``wifi_manager.py`` -- WiFi connection manager
* ``rainbow2.py`` -- color table for LED strip mode
* ``boot.py`` -- auto-start on boot (upload last)

Uploading with ampy
-------------------

Upload all files from the Cursor terminal (``boot.py`` last):

.. code-block:: bash

   cd micropython
   ampy --port /dev/cu.usbserial-0001 put wifi.dat
   ampy --port /dev/cu.usbserial-0001 put solar_flare_alert.py
   ampy --port /dev/cu.usbserial-0001 put wifi_manager.py
   ampy --port /dev/cu.usbserial-0001 put rainbow2.py
   ampy --port /dev/cu.usbserial-0001 put boot.py

Or as a single command:

.. code-block:: bash

   cd micropython && ampy --port /dev/cu.usbserial-0001 put wifi.dat && ampy --port /dev/cu.usbserial-0001 put solar_flare_alert.py && ampy --port /dev/cu.usbserial-0001 put wifi_manager.py && ampy --port /dev/cu.usbserial-0001 put rainbow2.py && ampy --port /dev/cu.usbserial-0001 put boot.py

If the board is running the old program
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If the old ``boot.py`` auto-starts the program, you need to stop it first:

1. Connect via screen: ``screen /dev/cu.usbserial-0001 115200``
2. Press ``Ctrl+C`` (maybe several times) to get the ``>>>`` REPL prompt
3. Wipe boot.py: ``f = open('boot.py', 'w'); f.write(''); f.close()``
4. Exit screen: ``Ctrl+A``, then ``K``, then ``Y``
5. Now upload files with ampy as described above

Verifying uploaded files
^^^^^^^^^^^^^^^^^^^^^^^^

Connect to the REPL and check file names and sizes:

.. code-block:: bash

   screen /dev/cu.usbserial-0001 115200

.. code-block:: python

   import os; [(f, os.stat(f)[6]) for f in os.listdir()]

Configuration
=============

In ``solar_flare_alert.py``, check if the options are correct, especially if the
LED pins are correct. The pin names on ESPs are a bit weird from time to time.

The ``boot.py`` file imports ``solar_flare_alert`` and calls ``_main()`` if
``RUN = True``. This makes the program start automatically when the board is powered.

Wiring
======
On our board the pins are labeled with **IOxx** so it is
pretty straight forward.
The pins deliver 3.3V and some sources say max 12mA, we use a 110 Ohm resistor.

For boards without a built-in status LED (e.g., ESP32-D), set
``STATUS_LED = None`` in ``solar_flare_alert.py`` for auto-detection,
or ``STATUS_LED = False`` to disable it entirely.

Testing
=======
In ``solar_flare_alert.py`` set ``RUN = False``,
the program loop won't run and you can test the functions from the REPL.

Connect to the REPL via ``screen /dev/cu.usbserial-0001 115200``, then:

.. code-block:: python

   import solar_flare_alert
   solar_flare_alert.test_goes_to_freq_duty()  # LED brightness/blink test

For more details on the development workflow, see ``micropython/DEVELOPMENT.md``.
