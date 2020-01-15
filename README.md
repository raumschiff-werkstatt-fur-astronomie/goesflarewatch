# GOES Flare Watch

This is an application to display with multiple front ends the state of activity of the Sun. 
It reads the last value delivered by the GOES spacecraft and sends it to an arduino or an esp32 processor,
which can then control different LEDs. 

For the python versions, part of the code is written in a jupyter notebook that organises the access to the GOES data and then transforms the value into a number that can be used by the arduino to control the LEDs. Finally, the notebook sends the value to the serial port of the computer. On the arduino side, a program gets the value from the serial port and sends it to the corresponding LED. 

The micropython version is very hand as it does everything ont the micriprocessor, no need for jupyter notebooks. 

## How to get started

There are several versions of this 

* The 4 LED version is the simplest. Best to get started
* You can increase the number of LEDs at your convenience. The changes should be obvious. I have a 4 and 8 LED version
* The one I am working now is a version that should work for LED strips, making the light color of your environment dependent on the solar activity. 
