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

3. If it **keeps blinking**, open the WiFi settings on your phone or computer and connect to the access point named **WifiManager**.

4. The phone should show a sign-in page. If it does not, open a web browser on the phone and type ``http://192.168.4.1`` in the address field. Stay on **WifiManager** while that page loads. If it still does not open, turn mobile data off and try again.

5. Choose your home WiFi network from the list and enter the password.

6. You're done! Reconnect your device to your normal WiFi. The solar flare alert will now show the Sun's activity level.

Earlier lamps
-------------

Lamps sold before this setup page was updated do not show a sign-in window. The phone can be connected to the lamp while the browser still cannot open the page. Try the following once.

1. Watch the LED. If it **stops blinking**, the lamp has already joined a saved network. Reconnect your phone to your home Wi-Fi. Nothing else is required.

2. If the LED **keeps blinking**, join the Wi-Fi network **WifiManager**. It is an open network and has no password.

3. Turn mobile data off, and stay on **WifiManager** when the phone says the network has no internet. Otherwise the phone sends the address through the mobile network, and the lamp never sees it.

4. On the phone, open a web browser and type ``http://192.168.4.1`` in the address field. Keep the ``http://``. Typing the number into a search box does not reach the lamp.

5. If the page does not load, turn the lamp off, wait ten seconds, turn it on, and repeat from step 2.

6. If the page is still blank, stop retrying. On these lamps the setup program accepts the Wi-Fi connection and then does not answer, whether the browser is on a phone or a computer. The lamp needs the updated setup program (``wifi_manager.py``) before it can be joined to a new network. A network it has already saved keeps working.
