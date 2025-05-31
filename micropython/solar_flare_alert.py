# Original version from  morgulbrut Tillo
# Modified in 2021 by A.Csillaghy for the new json format provided by NOAA
# Included also the wifi manager for connecting to different wireless LANs
# May 22 many changes for the ECSITE conference 2022
# Nov 22 many changes for support of the LED_STRIP
# Updated in March 2025 to use an improved Wi-Fi Manager ACs

"""
This is the main micropython program that runs on the ESP32 microprocessor.

It needs the boot.py program that will call it, and collaborates
with the wifi manager that handles the connection to a specific access point
"""

# TODO Now the new wifi_manager is included, needs testing with a new esp32 to see if it works better
# TODO Once this is tested, remove old wifimgr.py
# TODO Then make an own version of the script that creates the web page
# TODO enccrypt the json file

import gc
import time
from math import log

import machine  # needed for Hardware stuff
import ujson
import urequests
import rainbow2

import micropython
#import wifimgr

import sys
#sys.path.append('/libs/micropython-wifi_manager')  # Add the submodule path

from wifi_manager import WifiManager  # ✅ Updated to use wifi_manager.py


###################################
# CONFIGURATION SECTION

DEBUG = True  # more verbose output on the serial port
RUN = True  # set False for testing, True for running

if DEBUG:
    print("I am alive!")

FLARE_MODE = False
"""
FLARE mode vs solar activity configuration: if you want the LED to light up only when there
is a flare (e.g. larger than GOES_M), then you need to set up FLARE_MODE to True. Otherwise
the system will display the flare activity on the specified number of LEDS.
acs 30.11.22 : 
I am changing this. Flare mode should really be a mode for itself with a flare detection algorithm.
This is another todo. FLARE_MODE is therefore replaced with SINGLE_LED_MODE
"""
SINGLE_LED_MODE = True
LED_STRIP_MODE = False
"""
Now we also need to know what kind of hardware are we trying to drive. We have several 
modes. 
SINGLE_LED_MODE is used to display with PWM the information on a single LED. This is the mode of
the solar flare alert designed for the ECSITE conference
LED_STRIP_MODE is used to drive a RGB LED strip with different colors. Technically, it could also 
be used with the FLARE mode, but it is more to change colors depending on a specific solar activity. 
"""

GOES_LIMIT = log(1e-09)
GOES_X = log(1e-04) - GOES_LIMIT
GOES_M = log(1e-05) - GOES_LIMIT
GOES_C = log(1e-06) - GOES_LIMIT
GOES_B = log(1e-07) - GOES_LIMIT
GOES_A = log(1e-08) - GOES_LIMIT

STATUS_LED = 2
# Status LED uses the internal LED for
# - blinking while connecting to WiFi
# - on while getting data from the internet
# - off while waiting

# These are ESP32 dev board pins
if SINGLE_LED_MODE:
    LEDS = [27]
elif LED_STRIP_MODE:
    LEDS = [13, 12, 27]
else:
    # TODO this needs to be implemented, that is just a place holder
    LEDS = [13, 12, 27]
"""
The LEDS variable decides the action of the program
LEDS uses the GPIO, inorder to control the status of the LEDs.

In the current ECSITE 22 version, we use just one. 
The version with one single LED is usually good with the SINGLE_LED. 

TODO
The version with 4 LEDS would display the solar activity as a "scale" going from low to high, i.e. B,C,M,X

TODO
Possible would be also A,B,C,M,X
#LEDS = [16, 17, 21, 22, 25]

Finally, the program is also able to steer an entire LED strip to display the solar activity as an rgb value.
This requires the LED_STRIP_MODE and it uses 3 LED inputs, one for R, G and B, repectively. 

Please be aware that LED_STRIP_MODE requires additionally MOSFETS to bring 12 V to the LED strip. 
 
"""

# Default values for PWM:
DEFAULT_FREQ = 500
DEFAULT_DUTY = 1023
SLOW_BLINKING = 1
FAST_BLINKING = 3

# END OF CONFIGURATION SECTION
# ================================

if DEBUG:
    print("I am alive!")

if LED_STRIP_MODE:
    #     color_table = []
    #     f = open('rainbow.rgb')
    #     lines = f.readlines()
    #     for line in lines:
    #         color_table.append(line.strip().split())
    color_table = rainbow2
    if DEBUG:
        print("Color table loaded.")

status_led = machine.Pin(STATUS_LED, machine.Pin.OUT)

leds = []
for led in LEDS:

    if SINGLE_LED_MODE or LED_STRIP_MODE:
        # PWM is used for these modes
        this_led = machine.PWM(machine.Pin(led), freq=500, duty=1023)
        leds.append(this_led)
        if DEBUG:
            print("this_led, PWM freq, duty:", this_led, this_led.freq(), this_led.duty())
            # time.sleep(60)
    else:
        # just standard connection is used for the other cases
        leds.append(machine.Pin(led, machine.Pin.OUT))

if LED_STRIP_MODE:
    for line in color_table:
        print(line)
        for i in range(3):
            # why is duty inversed? No idea about this, but it works that way
            leds[i].duty(1023 - line[i] * 2)
            leds[i].freq(500)
            time.sleep(0.01)


# this is needed to start autonomously on the microcontroller
# if __name__ == "__main__":
#     if DEBUG:
#         print( "Start main program" )
#     _main()

def do_connect():
    """
    Connects to the network using the Wi-Fi Manager.
    If no network is found, it starts an Access Point for configuration.
    """
    
    wlan = WifiManager()
    wlan.connect()  # ✅ Updated to use new Wi-Fi Manager
    #wlan = network.WLAN(network.STA_IF)

    if wlan.is_connected():
        if DEBUG:
            print("Connected to Wi-Fi!")
            print("Network config:", wlan.get_address())
    else:
        print("Could not connect to Wi-Fi.")


def get_current_goes_val() -> float:
    """
    This function gets the GOES data from the Internet, more precisely from the services
    offered by NOAA. It gets the last part of the corresponding JSON file and extracts the
    value for the high channel of the XRS instrument.

    :return: the flux value as a real number.

    """

    # we do not need to read the entire file
    my_headers = {'Range': 'bytes=-2000'}

    try:
        response = urequests.get("https://services.swpc.noaa.gov/json/goes/primary/xrays-6-hour.json",
                                 headers=my_headers)
        text = response.text[:-1]
        response.close()
    except:
        # TODO: ESP32 correct heap memory management -- might not be necessary
        # There is a memory error handling necessary with the ESP. It has to do with filling up
        # the heap. However, this explicit garbage collection might not help too much. For now,
        # however this does allow to continue and re-read the file to get the correct number.
        # gc.collect()
        # gc.threshold(gc.mem_free() // 4 + gc.mem_alloc())
        # print('*** MEMORY ERROR ***')
        # micropython.mem_info()
        if DEBUG:
            print("Something went wrong, return 0")
        return 0

    if DEBUG:
        print('Response: ', text)

    # unfortunately, it is not fully deterministic when the high channel is at the correct position
    # to be extracted from the json. Therefore, we need to scan through the records in the response
    # to find the correct channel (i.e. 01-0.8nm)

    i = -1
    response_processed = text.split(", {")
    if DEBUG:
        print('\n Response processed: ', response_processed)

    while abs(i) < len(response_processed):

        return_value = 0.0
        try:
            #            response_processed = "{" + text.split(", {")[i]
            this_item = "{" + response_processed[i]
            if DEBUG:
                print('\n In loop: i, this item: ', i, this_item)

            response_json = ujson.loads(this_item)
            if response_json["energy"] == "0.1-0.8nm":
                return log(response_json["flux"]) - GOES_LIMIT

        except:

            # Brute force: ignore errors in the json file and wait for the next value
            if DEBUG:
                print("Wrong goes channel, returning 0")
            return 0

        i = i - 1

    return return_value

    # else:
    #     return response_json["flux"]


# ---------
def convert(x, i_m, i_M, o_m, o_M):
    """
    Will return an integer between out_min (o_m) and out_max (o_M)
    From the Internet: https://forum.micropython.org/viewtopic.php?f=2&t=7615
    """
    return max(min(o_M, (x - i_m) * (o_M - o_m) // (i_M - i_m) + o_m), o_m)


# ---------

def goes_to_freq_duty(val, rgb=False):
    """
    This function transforms the GOES values into frequency and duty cycles that can be used to control the
    Pulse Width Modulation, when operating a single LED. The idea behind this is that
    * If the value is less than GOES C, the LED lights at a minimal value
    * If the value is in the C domain, the LED increases continuously its intensity
    * If the value is in M, it blinks slowly
    * If the value is above X, it blinks strongly

    The range of the GOES value is assumed to be between 10-9 and 10-2 [W/m2]

    :param val: The GOES value
    :param rgb: Boolean variable to tell if rgb values are needed or just a single freq/duty
    :return: Values for `duty` and `frequency` - the values that can be used in the PWM module
    :rtype: (int, int)
    """

    if rgb:
        freq = [DEFAULT_FREQ, DEFAULT_FREQ, DEFAULT_FREQ]
        duty = [DEFAULT_DUTY, DEFAULT_DUTY, DEFAULT_DUTY]

        # TODO this has too many type conversions, color table should be corrected to 0..1023 and ints not stings
        duty_index = int(convert(val, GOES_B, GOES_M, 0, len(color_table) - 1))
        duty_rgb = color_table[duty_index]

        for i in range(3):
            # duty[i] = convert(int(duty_rgb[i]), 0, 255, 0, 1023)
            duty[i] = int(convert(duty_rgb[i], 0., 1., 0, 1023))

        if GOES_M < val < GOES_X:
            freq = [SLOW_BLINKING, SLOW_BLINKING, SLOW_BLINKING]
        elif val > GOES_X:
            freq = [FAST_BLINKING, FAST_BLINKING, FAST_BLINKING]

        if DEBUG:
            print("val, duty_index, duty_rgb, duty = ", val, duty_index, duty_rgb, duty)

    else:
        freq = DEFAULT_FREQ
        duty = DEFAULT_DUTY

        if GOES_C < val < GOES_M:
            # duty = int(round(val / 1e-6 * 80)) + 200
            # use now convert for calculating the duty 2022-11-27 ACs
            duty = int(convert(val, GOES_C, GOES_M, 0, 500))

        elif GOES_M < val < GOES_X:
            duty = 500
            freq = 1

        elif val > GOES_X:
            freq = FAST_BLINKING

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
    :rtype: object
    """

    if not LED_STRIP_MODE:

        if val is None:
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

    else:
        print(freq, duty)
        for i in range(3):
            leds[i].freq(freq[i])
            leds[i].duty(duty[i])


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

    if not SINGLE_LED_MODE:

        if not LED_STRIP_MODE:

            for led in leds:
                time.sleep(0.4)

        else:

            leds[0].freq(500)
            leds[1].freq(500)
            leds[2].freq(500)
            for color in color_table:
                for i in range(3):
                    this_duty = int(convert(int(color[i]), 0, 255, 0, 1023))
                    # print( "color, duty =  ", color[i], this_duty )
                    leds[i].duty(this_duty)
                    if DEBUG:
                        print("color, duty, leds[i] =  ", color[i], this_duty, leds[0].duty(), leds[1].duty(),
                              leds[2].duty())
            time.sleep(0.4)

    # TODO This works currently only for one LED in PWM mode. Needs to be done for any LED number

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

    do_connect()  # first establish wireless LAN connection
    boot_up()  # then start up the program

    # number of goes values to keep
    n_diff = 100
    diff = [0.0] * n_diff

    while RUN:

        #     if DEBUG: print_led_vals()

        status_led.on()

        # current_goes_val = get_current_goes_val(log_scale=not FLARE_MODE and not LED_STRIP_MODE)
        current_goes_val = get_current_goes_val()  # always in log scale
        if DEBUG:
            print('\n current GOES value: ', current_goes_val)

        if current_goes_val != 0:

            if SINGLE_LED_MODE or LED_STRIP_MODE:

                freq, duty = goes_to_freq_duty(current_goes_val, rgb=LED_STRIP_MODE)
                set_leds(freq=freq, duty=duty)

            else:

                diff[0:-1] = diff[1:]  # shift array to make space for the new value
                diff[-1] = current_goes_val
                if DEBUG:
                    print("Diff array is: ", diff)

                # TODO this needs to be revisited
                level = goes_to_int(current_goes_val,
                                    input_range=[min([i for i in diff if i > 0]), max(diff)])

                if DEBUG:
                    print('\n Level: ', level)
                # led_no = val_str2int(val, len(leds))

                set_leds(level)

        else:
            if DEBUG:
                print('\n No correct GOES val returned, skip this time')

        status_led.off()

        if DEBUG:
            print(current_goes_val)
        # TODO repair this
        #         print_led_vals()

        time.sleep(60)


_main()
