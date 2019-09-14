import machine  # needed for Hardware stuff
import urequests
import time
from math import log, ceil
import network

###################################
# Settings

DEBUG = False  # more verbose output on the serial port
RUN = True  # set False for testing, True for running
SSID = 'NETWORK'
PASSWORD = 'PASSWORD'

"""
Status LED
uses the internal LED:
- fast blinking while connecting to WiFi
- on while getting data from the internet
"""
STATUS_LED = 2

"""
LEDS
uses GPIO, in order
level 1 lights up LEDS[0]
"""
LEDS = [16, 17, 21, 22, 25]
###################################

status_led = machine.Pin(STATUS_LED, machine.Pin.OUT)
leds = []
for led in LEDS:
    leds.append(machine.Pin(led, machine.Pin.OUT))


def do_connect():
    """
    Connect to the network from the MicroPython manual:
    http://docs.micropython.org/en/v1.9.3/esp8266/esp8266/tutorial/network_basics.html
    """
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(SSID, PASSWORD)
        while not sta_if.isconnected():
            # blink LED while connecting
            status_led.on()
            time.sleep(0.05)
            status_led.off()
            time.sleep(0.05)
    print('network config:', sta_if.ifconfig())


def get_val():
    """
    Getting raw data from the internet

    Returns:
    str: raw data, last column of last row

    """

    # Get request to get the most recent table
    response = urequests.get(
        "https://services.swpc.noaa.gov/text/goes-xray-flux-primary.txt")
    return response.text.split(" ")[-1].strip()


def val_str2int(val, numLEDs=4):
    """
    Calculates the integer value to show based on the number of LEDs

    Parameters:
    val (str): Raw value
    numLEDs (int): number of LEDs

    Returns:
    int: Number of Leds to light up, -1 if error

    """
    try:
        return min(max(ceil(log(float(val), 10)+7), 0), numLEDs)
    except ValueError:
        return -1


def set_leds(val):
    """
    Sets the LEDs based on an integer value
    if the value is < 0 (error from val_str2int)
    it only sets the highest LED.

    Parameters:
    val (int): number of LEDs to light up
    """

    for led in leds:
        led.off()
    if val >= 0:
        for led in leds[:val]:
            led.on()
    else:
        leds[-1].on()


def boot_up():
    """
    Boot up animation, lights up every LED
    """

    for led in leds:
        led.on()
        time.sleep(0.4)
    for led in leds:
        led.off()
    print("bootup done")


def print_led_vals():
    """
    Prints out a list with the LED values
    """
    lp = []
    for led in leds:
        lp.append(led.value())
    print(lp)


do_connect()
boot_up()

while(RUN):
    if DEBUG:
        print_led_vals()

    status_led.on()
    val = get_val()
    led_no = val_str2int(val, len(leds))
    set_leds(led_no)
    status_led.off()

    if DEBUG:
        print(val)
        print(led_no)

    print_led_vals()
    time.sleep(60)
