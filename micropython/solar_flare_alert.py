# Original version from  morgulbrut Tillo
# Modified in 2021 by A.Csillaghy for the new json format provided by NOAA
# Included also the wifi manager for connecting to different wireless LANs
# May 22 many changes for the ECSITE conference 2022

"""
This is the main micropython program that runs on the ESP32 microprocessor.

It needs the boot.py program that will call it, and collaborates
with the wifi manager that handles the connection to a specific access point
"""

import gc
import time
from math import log

import machine  # needed for Hardware stuff
import ujson
import urequests

import micropython
import wifimgr


###################################
# First, let us look at the settings

DEBUG = True  # more verbose output on the serial port
RUN = True  # set False for testing, True for running

if DEBUG:
    print("I am alive!")

FLARE_MODE = True
"""
FLARE mode vs solar activity configuration: if you want the LED to light up only when there
is a flare (e.g. larger than GOES_M), then you need to set up FLARE_MODE to True. Otherwise
the system will display the flare activity on the specified number of LEDS.
"""

GOES_X = 1e-04
GOES_M = 1e-05
GOES_C = 1e-06
GOES_B = 1e-07

STATUS_LED = 2
# Status LED uses the internal LED for
# - blinking while connecting to WiFi
# - on while getting data from the internet
# - off while waiting

LEDS = [27]
"""
The LEDS variable decides the action of the program
LEDS uses the GPIO, inorder to control the status of the LEDs.

In the current ECSITE 22 version, we use just one. 
The version with one single LED is usually good with the FLARE MODE. 

With 4 LEDS, you would use e.g.
#LEDS = [13, 12, 14, 27]

Possible is also:
#LEDS = [16, 17, 21, 22, 25]

"""

status_led = machine.Pin(STATUS_LED, machine.Pin.OUT)

leds = []
for led in LEDS:
    if FLARE_MODE:
        this_led = machine.PWM(machine.Pin(27), freq=1, duty=512)
        leds.append(this_led)
        if DEBUG:
            print("PWM freq, duty:", this_led.freq(), this_led.duty())
    else:
        leds.append(machine.Pin(led, machine.Pin.OUT))

if __name__ == "__main__":
    _main()

def do_connect():
    """
    Connects to the network using the Wifi Manager. It actually just sends the program control to this
    other module.
    """

    wlan = wifimgr.get_connection()
    if wlan is None:
        print("Could not initialize the network connection.")
    #         while True:
    #             pass  # you shall not pass :D
    # ACS May 22, this has been commented out because it can lead to a deadlock

    if DEBUG:
        print("ESP OK")
        print('network config:', wlan.ifconfig())


def get_current_goes_val(log_scale=True):
    """
    This function gets the GOES data from the Internet, more precisely from the services
    offered by NOAAA. It gets the last part of the corresponding JSON file and extracts the
    value for the high channel of the XRS instrument.

    :param log_scale: returns the value in a logarithmic sale. Default is True
    :return: the flux value as a real number.

    """

    # we do not need to read the entire file
    my_headers = {'Range': 'bytes=162000-164000'}

    try:
        response = urequests.get("https://services.swpc.noaa.gov/json/goes/primary/xrays-6-hour.json",
                                 headers=my_headers)
        text = response.text[:-1]
        response.close()
    except:
        # TODO: ESP32 correct heap memory management
        # There is a memory error handling necessary with the ESP. It has to do with filling up
        # the heap. Howevert, this explicit garbage collection might not help too much. For now,
        # however this does allow to continue and re-read the file to get the correct number.
        gc.collect()
        gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())
        print('*** MEMORY ERROR ***')
        micropython.mem_info()
        return 1e-09

    if DEBUG:
        print('Response: ', text)

    # unfortunately, it is not fully deterministic when the high channel is at the correct position
    # to be extracted from the json. Therefore, we need to scan through the records in the response
    # to find the correct channel (i.e. 01-0.8nm)

    i = -1
    while True:

        try:
            response_processed = "{" + text.split(", {")[i]
            if DEBUG:
                print('Response processed: ', response_processed)
            response_json = ujson.loads(response_processed)
            if response_json["energy"] == "0.1-0.8nm":
                break

        except:
            if DEBUG:
                print("Wrong goes channel, re-reading")

        i = i - 1
    # TODO: remove unnecessary garbage collection
    # Let's do some more garbage collection, but this is probably too much.
    # We probably can take this away.
    gc.collect()
    gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())
    if DEBUG:
        micropython.mem_info()
        print('-----------------------------')
        print('free: {} allocated: {}'.format(gc.mem_free(), gc.mem_alloc()))
        print('-----------------------------')

    if log_scale:
        return abs(log(response_json["flux"]))
    else:
        return response_json["flux"]


# ----------

def goes_to_freq_duty(val):
    """
    This function transforms the GOES values into frequency and duty cycles that can be used to control the
    Pulse Width Modulation, when operating a single LED. The idea behind this is that
    * If the value is less than GOES C, the LED lights at a minimal value
    * If the value is in the C domain, the LED increases continuously its intensity
    * If the value is in M, it blinks slowly
    * If the value is above X, it blinks strongly

    :param val: The GOES value
    :return: Values for `duty` and `frequency` - the values that can be used in the PWM module
    :rtype: (int, int)
    """

    if val < GOES_C:
        freq = 500
        duty = 200

    if GOES_C < val < GOES_M:
        duty = int(round(val / 1e-6 * 80)) + 200
        freq = 500

    elif val > GOES_M and val > GOES_X:
        duty = 1023
        freq = 1

    else:
        duty = 1023
        freq = 3

    if DEBUG:
        print("freq, duty =", freq, duty)

    return freq, duty


# ----------

def goes_to_int(val, nb_LED=4, debug=True, input_range=[1e-8, 1e-7]):
    """
    Calculates the integer value to show based on the number of LEDs. This is the function called
    when there are more than one LED to control, i.e. when we build an LED "scale". Technically,
    this is important as we do not use the PWM in this case

    :param val: GOES value
    :type val: float

    :param nb_LED: number of LEDs
    :type nb_LED: int

    :return: Number of LEDs to light up, -1 if error
    :rtype: int
    """

    try:
        if DEBUG: print('value entered = ', val)

        range = abs(input_range[1] - input_range[0])

        if range > 0:
            slope = float(nb_LED) / (range)
        else:
            slope = 0

        # val = min(max(ceil(log(float(val), 10)+7), 0), numLEDs)
        # val = int(round( np.interp( val, input_range, [0,nb_LED-1])))
        val = int(round(slope / val + 1))

        if DEBUG:
            print('range, solpe, val = ', range, slope, val)

        return val

    except ValueError:

        return -1


def set_leds(val=None, duty=512, freq=500):
    """
    Sets the LEDs based on an integer value
    if the value is < 0 (error from val_str2int)
    it only sets the highest LED.

    Parameters:
    val (int): number of LEDs to light up
    """

    if val == None:
        leds[0].freq(freq)
        leds[0].duty(duty)
        return

    for led in leds:
        led.off()
    if val >= 0:
        for led in leds[:val]:
            led.on()
    else:
        leds[-1].on()


def blink_led(val):
    """
    :meta private:
    This is work in progress.
    """
    # TODO needs to program this correctly

    #     if val==0: delay
    #         case 0: delay = 0.1
    #         case 1: delay = 1
    #         case 2: dela = 2
    #         case 3: time = 100
    #
    led.off()
    time.sleep(time)


def boot_up():
    """
    :meta private:
    Boot up animation, lights up every LED. In PWM mode, blink the output LED.
    """

    # TODO This works currently only for one LED in PWM mode. Needs to be done for any LED number

    for led in leds:
        #         led.on()
        time.sleep(0.4)

    time.sleep(10)

    #     for led in leds:
    #         led.off()
    if DEBUG:
        print("Bootup done")


def print_led_vals():
    """
    :meta private:
    This is a helper program that prints out on the console a list with the LED values.
    This is usually used only in debug mode and connected to a terminal or Thonny
    """
    lp = []
    for led in leds:
        lp.append(led.value())
    print('LED vals: ', lp)


def _main():
    """
    :meta private:
    This program starts the pipeline that runs on the microprocessor.
    """

    do_connect()  # first go to the wireless LAN
    boot_up()  # then start up the program

    n_diff = 100
    diff = [0.0] * n_diff

    while RUN:

        #     if DEBUG: print_led_vals()

        status_led.on()

        current_goes_val = get_current_goes_val(log_scale=not FLARE_MODE)

        if FLARE_MODE:

            freq, duty = goes_to_freq_duty(current_goes_val)
            set_leds(freq=freq, duty=duty)


        else:

            diff[0:-1] = diff[1:]  # shift array to make space to the new value
            diff[-1] = current_goes_val
            if DEBUG: print("Diff array is: ", diff)

            level = goes_to_int(current_goes_val,
                                input_range=[min([i for i in diff if i > 0]), max(diff)])

            if DEBUG: print('level: ', level)
            # led_no = val_str2int(val, len(leds))

            set_leds(level)
        #     set_leds(0)

        status_led.off()

        if DEBUG:
            print(current_goes_val)
        # TODO repair this

        #         print_led_vals()

        time.sleep(60)
