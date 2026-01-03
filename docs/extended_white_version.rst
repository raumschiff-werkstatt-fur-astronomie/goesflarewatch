How to use the Solar Flare Alert - Extended White Version
=========================================================

.. figure:: images/img.png
   :width: 400

What you have in your kit:

* A table tennis ball
.. figure:: images/IMG_2586.jpg
   :width: 100

* One white breadboard
.. figure:: images/IMG_2556.jpg
   :width: 100

* Wires
.. figure:: images/IMG_2562.jpg
   :width: 100

* One LED with an LED holder
.. figure:: images/IMG_2564.jpg
   :width: 100

* One wire holder
.. figure:: images/IMG_2557.jpg
   :width: 100

* One ESP32 development board
.. figure:: images/IMG_2587.jpg
   :width: 100

* One 110 Ohm resistor
.. figure:: images/IMG_2566.jpg
   :width: 100

* One lamp stand
.. figure:: images/IMG_2559.jpg
   :width: 100

* A USB cable and power adapter
.. figure:: images/IMG_2567.jpg
   :width: 100



Assembling the device
---------------------
1. Insert the ESP32 development board onto the breadboard.

.. figure:: images/IMG_2571.jpg
   :width: 400

2. Mount the wire holder with LED onto the breadboard, leaving one breadboard slot on both sides

.. figure:: images/IMG_2572.jpg
   :width: 400


3. Place the resistor into a free space on the breadboard, and connect it to the free space above or below the LED holder.

.. figure:: images/IMG_2574.jpg
   :width: 400

4. Locate pin **27** on the ESP32 development board. Connect a wire from **pin 27** of the ESP32 to one of the free slot in the same breadboard column as the resistor.

.. figure:: images/IMG_2575.jpg
   :width: 400

6. Connect a wire from a **GND pin** of the ESP32 to the other free slot below the LED holder.

.. figure:: images/IMG_2585.jpg
   :width: 400

7. Take the table tennis ball and make a small hole large enough to mount the LED holder. (Some versions have the hole already prepared.)

.. figure:: images/IMG_2569.jpg
   :width: 400

8. Insert the LED into the LED holder. Note that the LED legs have different lengths.
then place the holder into the hole in the tennis ball.

.. figure:: images/IMG_2570.jpg
   :width: 400

9. Insert th isolation tube over the wires that have a female plug.

.. figure:: images/IMG_2578.jpg
   :width: 400

10. Connect a wire to each leg of the LED. Remember the color of the
cables that connects to the short leg LED.

.. figure:: images/IMG_2581.jpg
   :width: 400

11. Assemble the wire holder, attaching one LED wire to each side.
Ensure that the **long leg of the LED (anode)** is connected to the **resistor side**, and the **short leg (cathode)** goes to **ground**.

12. Insert the USB cable into the board, and plug it in. The LED should blink.

Your solar flare alert is now physically assembled and ready to connect to the WiFi.

Note: the isolation tubes can be settled by warming them. They will reduce their size.
.. include:: wifi_connection.rst

