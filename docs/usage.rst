How to Use the Solar Flare Alert
================================

Assembling the Device
---------------------

Here are all the components of the device:
   .. figure:: ./images/IMG_1751.jpeg
      :width: 400px
      :align: center
      :alt: Wire ring inserted in socket strip

1. Insert the wire ring in the center of the socket strip and insert the LED into the ping-pong ball.

   .. image:: ./images/IMG_1752.jpeg
      :width: 400px
      :align: center
      :alt: LED placed inside ping-pong ball

2. Plug the cables into the outer plugs of the socket strip.
   Ensure the **black cable is on the left side** when viewed from the perspective of the ESP32.

   .. image:: images/IMG_1753.jpeg
      :width: 400px
      :align: center
      :alt: Cables correctly inserted in socket strip

Make sure the black cable goes to the left side, marked with a black marker

   .. image:: images/IMG_1754.jpeg
      :width: 400px
      :align: center
      :alt: USB cable plugged in

3. Plug in the USB cable to power the device.

   .. image:: images/IMG_1755.jpeg
      :width: 400px
      :align: center
      :alt: Fully assembled Solar Flare Alert device

Your solar flare alert is now physically assembled and ready to connect to the WiFi.

Connecting to the WiFi
----------------------

1. Turn the lamp on by plugging in the USB cable. The lamp should blink.

2. Watch the LED. If it **stops blinking**, the lamp has already joined a saved network. Reconnect your phone to your home Wi-Fi. Nothing else is required.

3. If the LED **keeps blinking**, use a smartphone or a computer to join the Wi-Fi network **WifiManager**. It is an open network and has no password.

4. On the phone, open a web browser and type ``http://192.168.4.1`` in the address field. Keep the ``http://``. Typing the number into a search box does not reach the lamp.

5. If the page does not load, turn the lamp off, wait ten seconds, turn it on, and repeat from step 3.

6. The page lists every network it can reach. Choose your own and enter the password.

7. The device saves the password, restarts, and tries to join your network.

8. If the LED stays lit, the connection was successful.

9. You are done. If this has not already happened automatically, you can connect your phone or your computer back to your normal Wi-Fi. The solar flare alert now shows the Sun's current activity level.
