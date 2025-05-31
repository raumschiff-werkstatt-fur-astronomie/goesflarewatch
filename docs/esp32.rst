How to Set Up the ESP32 Version
===============================

If you are looking for the necessary MicroPython programs,
here they are:

- `solar_flare_alert.py <https://raw.githubusercontent.com/raumschiff-werkstatt-fur-astronomie/goesflarewatch/master/micropython/solar_flare_alert.py>`_ :
  Contains the program that controls the LED, including the connection and processing of the data from the GOES data center.

- `wifimgr.py <https://raw.githubusercontent.com/raumschiff-werkstatt-fur-astronomie/goesflarewatch/master/micropython/wifimgr.py>`_:
  Contains the program that allows connecting the
  solar flare alert to a WiFi network.

There are two versions of the kit available:

1. The first version utilizes a white breadboard for assembling the components.
2. The second version uses a green breadboard circuit board and requires soldering, but it is more compact.

Both versions rely on an ESP32 microprocessor development board.
Before proceeding, you will need to install MicroPython on the
microprocessor and transfer the following two programs:

- **solar_flare_alert.py**:
- **wifi_mgr.py**:

.. toctree::
   :maxdepth: 3

   source/mp_install_esp32
   source/white_breadboard
   source/green_breadboard
