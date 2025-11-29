How to work with the ESP32 solar flare alert micropython programs
=================================================================

There is one micropython program necessary for the solar flare alert lamp:

- `solar_flare_alert.py <https://raw.githubusercontent.com/raumschiff-werkstatt-fur-astronomie/goesflarewatch/master/micropython/solar_flare_alert.py>`_ :
  Contains the program that controls the LED, including the connection and processing of the data from the GOES data center.

The other important program is the wifi manager which allows to connect the device to the Internet.
This is an external program tough, but is part of the library.
- `wifimgr.py <https://raw.githubusercontent.com/raumschiff-werkstatt-fur-astronomie/goesflarewatch/master/micropython/wifimgr.py>`_:
  Contains the program that allows connecting the
  solar flare alert to a WiFi network.

Note that you find on GitHub also other programs for other platforms, such as Arduino and Raspberry PIs,
but a lot of these are not actively maintained.

Concerning the hardware, as shownt in the assembling instructions, there
are two versions of the kit available:

1. The first version utilizes a white breadboard for assembling the device, please refer
to these instructions for putting it together.
2. The second version uses a green breadboard circuit board. If you do not have the
version already soldered, you can do it yourself.

The versions are based on the ESP32 microprocessor development board.
They come with the programs installed. Of course you can modify the programs yourself
and interact with the board completely freely. How you do this is described in
numerous platforms, see for instance xxx.

For the complete installation instructions of the solar flare alert software,
please see these instructions.


.. toctree::
   :maxdepth: 3

   source/mp_install_esp32
   source/white_breadboard
   source/green_breadboard
