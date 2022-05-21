.. Bla documentation master file, created by
   sphinx-quickstart on Wed Dec 23 16:36:22 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.
==============================================
Welcome to the Solar Flare Alert documentation!
==============================================

Solar Flare Alert (formerly called goesflarewatch) is a set of applications
to display the state of activity of the Sun using diverse hardware front ends,
including arduino, and ESP32 to light up LEDs.

The back end reads the last value delivered by the GOES spacecraft
and sends it to the processor, which then controls the LEDs in customizable
manner.

For There is a python versions, part of the code is written in a
jupyter notebook that organises the access to the GOES data and
then transforms the value into a number that can be used by the
arduino to control the LEDs.
Finally, the notebook sends the value to the serial port of the computer.
On the arduino side, a program gets the value from the serial port and
sends it to the corresponding LED.

The micropython version is very handy
as it does everything ont the microprocessor,
no need for the jupyter notebooks.

The Raspberry PI version is still in construction.

Note that all these programs are continuously updated. This is a tinkering
project, and everyone is welcome to contribute!

How to get started
==================

There are several versions of this

* The micropython version is designed for the ESP32. **This is the one to use at the ECSITE 2022 conference**
* The 4 LED version is the simplest. Best to get started
* You can increase the number of LEDs at your convenience. The changes should be obvious. I have a 4 and 8 LED version
* The one I am working now is a version that should work for LED strips, making the light color of your environment dependent on the solar activity.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   summary
   code


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
