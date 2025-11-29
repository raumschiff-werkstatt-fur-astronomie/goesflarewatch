How to use the Solar Flare Alert - White Version
================================================

.. figure:: /images/img.png
   :width: 400

What you have in your kit:

* A table tennis ball
* One white breadboard
* Wires
* One LED with an LED holder
* One wire holder
* One ESP32 development board
* One 110 Ohm resistor

Assembling the device
---------------------
1. Take the table tennis ball and make a small hole large enough to mount the LED holder.
2. Connect a wire to each leg of the LED.
3. Insert the LED into the LED holder, then place the holder into the hole in the tennis ball.
4. Assemble the wire holder, attaching one LED wire to each side.
   Ensure that the **long leg of the LED (anode)** is connected to the **resistor side**, and the **short leg (cathode)** goes to **ground**.
5. Mount the wire holder with LED onto the breadboard.
6. Locate pin **27** on the ESP32 development board.
7. Plug the ESP32 development board into the breadboard.
8. Connect a wire from a **GND pin** of the ESP32 to the **ground rail** of the breadboard.
9. Place the resistor into a free space on the breadboard.
10. Connect a wire from **pin 27** of the ESP32 to one end of the resistor.
11. Connect the other end of the resistor to one side of the wire holder (the LED’s long leg / anode).
12. Connect a wire from the **ground rail** of the breadboard to the other side of the wire holder (LED short leg / cathode).

Your solar flare alert is now physically assembled and ready to connect to the WiFi.

.. include:: wifi_connection.rst
