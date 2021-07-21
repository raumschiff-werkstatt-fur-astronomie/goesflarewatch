# Original version from :
# Modified by A.Csillaghy for the new json format provided by NOAA

# This software 

import machine  # needed for Hardware stuff
import urequests
import usocket
import time
from math import log, ceil
import network
import ujson
import gc
#import urllib.urequest


###################################
# Settings

DEBUG = True  # more verbose output on the serial port
RUN = True  # set False for testing, True for running

# SSID = 'Raumschiff'
# PASSWORD = '70524761197483070928'
#SSID='Topinambour'
#PASSWORD='57z0kmnvze8e8'

SSID = 'Raumschiff'
PASSWORD = '70524761197483070928'
# SSID = 'csillag'
# PASSWORD = '50768316143033105816'


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
#This is the version with 4 LEDS
#LEDS = [16, 17, 21, 22, 25]
#LEDS = [13, 12, 14, 27]

#This is the version with one single LED, usually done for the FLARE MODE. 
LEDS = [27]

status_led = machine.Pin(STATUS_LED, machine.Pin.OUT)
leds = []
for led in LEDS:
    leds.append(machine.Pin(led, machine.Pin.OUT))
    
"""
FLARE mode vs activity confinguration: if you want the LED to light up only when there
is a flare (i.e. larger than GOES M), then you need to set up the FLARE mode. Otherwise
the system will display the flare activity on the specified number of LEDS.

"""
FLARE_MODE = True
M_FLARE=1e-05
C_FLARE=1e-06
B_FLARE=1e-07

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


def get_current_goes_val( log_scale=True ):

    """
    Getting raw data from the internet

    Returns:
    str: raw data, last column of last row

    """

    # Get request to get the most recent table

    #response = urequests.get('https://services.swpc.noaa.gov/json/goes/primary/xrays-6-hour.json')
    #    "https://services.swpc.noaa.gov/text/goes-xray-flux-primary.txt")
    #response = response.text.split("{")[-1].strip()

    myHeaders = {'Range':'bytes=78000-79000'}
    response = urequests.get("https://services.swpc.noaa.gov/json/goes/primary/xrays-6-hour.json", 
                            headers=myHeaders).text
    
    print('reponse: ', response)

# unfortunately, it is not deterministic when the high channel is at the correct position in the json.
# therefore, we need to scan through the records in the response to find the correct channel (i.e. 01-0.8nm)

    i=-2
    while True:

        response_processed = "{" + response.split(", {")[i]
    
        print('reponse processed: ', response_processed)

        response_json = ujson.loads( response_processed )
    
        if response_json["energy"] == "0.1-0.8nm" : break
            
        print( "wrong goes channel, re-reading")
        
        i = i-1


    print('response json:', response_json )
    
    if log_scale:
        return abs(log(response_json["flux"]))
    else:
        return response_json["flux"]
    

#----------

def goes_to_int(val, nb_LED=4, debug=True, input_range=[1e-8, 1e-7]):

    """
    Calculates the integer value to show based on the number of LEDs

    Parameters:
    val (str): Raw value
    numLEDs (int): number of LEDs

    Returns:
    int: Number of Leds to light up, -1 if error

    """

    try:
        if DEBUG: print('value entered = ', val)
        
        range = abs( input_range[1]-input_range[0] )
        
        if range > 0:
            slope = float(nb_LED)/(range)
        else:
            slope=0
        
        #val = min(max(ceil(log(float(val), 10)+7), 0), numLEDs)
        #val = int(round( np.interp( val, input_range, [0,nb_LED-1])))
        val = int(round( slope/val + 1 ))
        
        if DEBUG :
            print( 'range, solpe, val = ', range, slope, val )

        return val
    
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
    print('LED vals: ', lp)


do_connect()
boot_up()

n_diff=100
diff = [0.0]*n_diff


while(RUN):
    
    if DEBUG: print_led_vals()

    status_led.on()
    
    current_goes_val = get_current_goes_val( log_scale=not FLARE_MODE )
    
    if FLARE_MODE:

        if current_goes_val > B_FLARE :
            level=1
        else:
            level=0
        
    else:
        
        diff[0:-1] = diff[1:]      # shift array to make space to the new value
        diff[-1] = current_goes_val
        if DEBUG: print( "Diff array is: ", diff )
    
    
        level = goes_to_int( current_goes_val,
                         input_range = [min([i for i in diff if i > 0]), max(diff)])

    
    if DEBUG : print('level: ', level)
    #led_no = val_str2int(val, len(leds))
    
    set_leds(level)

    status_led.off()

    if DEBUG: print(current_goes_val)

    print_led_vals()
    
    gc.collect()
    gc.mem_free()

    time.sleep(60)
