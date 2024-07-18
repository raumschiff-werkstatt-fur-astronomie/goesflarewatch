How to Set Up the ESP32 Version
===============================

If you are looking for the necessary MicroPython programs,
here they are:

- `solar_flare_alert.py <https://raw.githubusercontent.com/raumschiff-werkstatt-fur-astronomie/goesflarewatch/master/micropython/solar_flare_alert.py>`_ :
Contains the program that controls the LED, including the
connection and processing of the data from the GOES data center.

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
- **wifimgr.py**:
.. toctree::
   :maxdepth: 3

   mp_install_esp32
   white_breadboard
   green_breadboard

Usage
=====

Once you have assembled the board,
you will need to connect to your local WiFi network.
Follow these steps:

1. Power on the solar flare alert. The indicator lamp will start
blinking.

2. If the blinking stops after a while, it means the solar flare alert
has successfully connected to a known network, and you are
ready to proceed.

3. If the blinking continues, access the list of WiFi networks on
your device and locate the WifiMgr access point. Connect to it.

4. Once connected, open a web browser and enter the address
**192.168.4.1**.

5. After a moment, you should see a list of available access points.
Select your desired network and enter the password.

6. That's it! You can now reconnect to your regular WiFi network.

After completing these steps, the solar flare alert will indicate
the level of solar activity.
