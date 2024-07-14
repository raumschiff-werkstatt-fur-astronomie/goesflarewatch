===============================================
Welcome to the Solar Flare Alert documentation!
===============================================

Solar Flare Alert, formerly known as goesflarewatch, is a tool designed to monitor the Sun's activity
using various hardware back ends, including an ESP32 microprocessor, for control of diverse LEDs

The system fetches current data values from the
`GOES spacecraft <https://www.swpc.noaa.gov/products/goes-x-ray-flux>`_,
which is then processed and routed to either a singular LED or an LED strip.
The illumination and color patterns of the LED(s) change dynamically, visually representing the current solar activity.

The two supported front ends currently implemented are:
* A single LED that gradually brightens with increasing solar activity.
It initiates a blinking pattern when a flare larger than the M-class occurs,
and the blinking gets faster for X-class flares.
* An LED strip that varies color based on the intensity of the solar activity.

The project utilizes `micropython` aimed at running directly on the ESP32 microprocessor.
All you need to get started is installing `micropython` on your ESP32 and downloading the relevant files.

Please note, the Python code for the Arduino is deprecated and will be revisited in due course.

..  Theoretically, part of the code is written in a
    jupyter notebook that organises the access to the GOES data and
    then transforms the value into a number that can be used by the
    arduino to control the LEDs.
    Finally, the notebook sends the value to the serial port of the computer.
    On the arduino side, a program gets the value from the serial port and
    sends it to the corresponding LED.

The Raspberry PI version is under construction.

We continually update all these programs as this project is a constant work in progress.
This is a tinkering
project, contributions are always welcome!

Getting Started
==================

We have different versions to cater to different requirements:

* **Micropython Version** (Recommended for the ESWW 2024 conference):
  Specifically designed for the ESP32.
* **LED Strip Version**:
  This version adjusts the color of the LED strip based on solar activity, using a specific color map.
* **4 LED Version**:
  A simplified version that displays the B,C,M,X activity with 4 LEDs
* **Multi-LED Versions**:
  For those seeking to expand beyond 4 LEDs. Changes to accommodate more LEDs should not to be too hard to do.
    We provide an implementation for 8 LEDs.



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
