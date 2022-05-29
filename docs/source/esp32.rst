How to use the ESP32 version
============================

There are two versions of the kit. The first version uses a white breadboard to assemble the components.
The second version uses a green breadboard circuit board, and needs soldering (but is more compact).

Both rely on an ESP32 microprocessor development board. Beforehand, you need to install Micropython on the
microprocessor and transfer two programs called main.py and wifimgr.py:

* main.py contains the program that connects to the spacecraft data centers;
* wifimgr.py contains the program that allows to connect the solar flare alert to a WIFI network.

.. toctree::
   :maxdepth: 3

   white_breadboard
   green_breadboard

Usage
=====

Once you have assembled the board, you will have to first connect to the local WIFI network. This is
done as follows:

#. Power on the solar flare alert. The lamp starts blinking
#. If the lamp stops bliking after a while, that means the solar flare alert found a known network and connected, so you are all set.
#. If the lamps continues blinking, go tho the list of WIFI networks and locate the WifiMgr access point. Connect to it.
#. Once connected, go into a browser and type the address 192.168.4.1
#. Afer a while, you should see the list of access points available. Select the one you want to connect, and type in your password
#. That's it. Now you can conect back to your regular network.