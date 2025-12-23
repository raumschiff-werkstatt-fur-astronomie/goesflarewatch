How to Use the Solar Flare Alert
================================

Assembling the Device
---------------------

Here are all the components of the device:
   .. figure:: ./images/IMG_1751.jpeg
      :width: 400px
      :align: center
      :alt: Wire ring inserted in socket strip

1. Insert the wire ring in the center of the
socket strip and insert the LED into the ping-pong ball.

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
------------------

1. Power on the solar flare alert. The LED will start blinking.

2. If the blinking **stops after a few seconds**, the device successfully connected to a known WiFi network.

3. If it **keeps blinking**, open the WiFi settings on your phone or computer and connect to the access point named **WifiMgr**.

4. Open a web browser and navigate to: ``192.168.4.1``

5. Choose your home WiFi network from the list and enter the password.

6. You're done! Reconnect your device to your normal WiFi. The solar flare alert will now show the Sun's activity level.
