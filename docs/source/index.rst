===============================================
Welcome to the Solar Flare Alert documentation!
===============================================

Solar Flare Alert (formerly called goesflarewatch) is an application
to display the state of activity of the Sun using diverse hardware back ends,
including ESP32 and formerly Arduino, to light up LEDs.

The back end reads the last value delivered by the
`GOES spacecraft <https://www.swpc.noaa.gov/products/goes-x-ray-flux>`_
and sends it to the processor, which then controls the LEDs in a customizable
manner.

The two currently existing front ends are:

* A single LED which gets increasingly bright as the solar activity increases, and starts blinking when a flare larger than the M-class happens, blinking even faster for X-class flares.
* An LED strip that changes color according to the intensity of the solar activity.

The code is written in micropython, it does everything on the ESP32
microprocessor. You can just install micropython on your
ESP32, download two files, and off you go!

The python code for the Arduino is deprecated.
I'll get back to this eventually.

..  Theoretically, part of the code is written in a
    jupyter notebook that organises the access to the GOES data and
    then transforms the value into a number that can be used by the
    arduino to control the LEDs.
    Finally, the notebook sends the value to the serial port of the computer.
    On the arduino side, a program gets the value from the serial port and
    sends it to the corresponding LED.

The Raspberry PI version is still in construction.

Note that all these programs are continuously updated. This is a tinkering
project, and everyone is welcome to contribute!

How to get started
==================

There are several versions available

* The micropython version is designed for the ESP32. **This is the one to use at the ECSITE 2022 conference**
* The 4 LED version is the simplest. Best to get started
* You can increase the number of LEDs at your convenience. The changes should be obvious. I have a 4 and 8 LED version
* The one I am working now is a version that should work for LED strips, making the light color of your environment dependent on the solar activity.


.. toctree::
   :maxdepth: 3
   :caption: Contents

   introduction
   esp32
   modules


Indices and tables
==================

* :ref:`genindex`
* :ref:`mod
* :ref:`search`
