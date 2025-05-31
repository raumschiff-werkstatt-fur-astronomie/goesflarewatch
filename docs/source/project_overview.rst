Overview of the System
----------------------

Solar Flare Alert is a set of applications designed to monitor the Sun's activity using various hardware backends, including the **ESP32 microprocessor**, which controls diverse LEDs. This system fetches real-time data from the **GOES spacecraft** and processes it to
dynamically adjust the LEDs, either through brightness or color changes, visually representing solar activity.

The system uses the **GOES spacecraft** data to fetch the solar activity levels, and it controls the LED(s) based on this data. The two main front-end versions currently implemented are:

1. **Single LED Version**: A single LED gradually brightens with increasing solar activity. It blinks when a flare larger than the M-class occurs, and the blinking speeds up for X-class flares.

2. **LED Strip Version**: An LED strip that varies in color according to the intensity of solar activity.

The project uses **Micropython**, specifically running on the **ESP32**,
which is very efficient as it requires no external processing (e.g., Jupyter notebooks).
You can install **Micropython** directly onto the ESP32, download the necessary files,
and get started right away. Check out `<esp32.html>`_.

While there is a **Python version** of the code for Arduino (which is now deprecated), it involves using a Jupyter notebook to fetch the data from the GOES spacecraft, process it, and send it to an Arduino via the serial port. The Arduino then controls the LEDs based on the received values.

A **Raspberry Pi** version is still under development.

All these programs are continuously updated as part of the tinkering nature of the project, and contributions are always welcome.

A Note About Updates
--------------------

We are continually updating these programs, as this project is always evolving. It's a tinkering project, and we encourage everyone to contribute!
