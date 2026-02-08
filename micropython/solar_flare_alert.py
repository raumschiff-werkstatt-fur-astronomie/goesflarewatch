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

import gc  # noqa: F401 - used by MicroPython runtime
import time
from math import log

import machine  # needed for Hardware stuff
import ujson
import urequests
import rainbow2

import micropython  # noqa: F401 - used by MicroPython runtime

# import wifimgr

import sys  # noqa: F401 - used by MicroPython runtime

# sys.path.append('/libs/micropython-wifi_manager')  # Add the submodule path

from wifi_manager import WifiManager  # noqa: E402


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

# Status LED configuration for compatibility with both old and new ESP32 boards
# Set to None to auto-detect (tries pin 2, common for ESP32 built-in LED)
# Set to a pin number (e.g., 2) to explicitly use that pin
# Set to False to disable status LED completely
# Status LED uses the internal LED for:
# - blinking while connecting to WiFi
# - on while getting data from the internet
# - off while waiting
# For ESP32-D boards without built-in LED, auto-detection will fail gracefully
STATUS_LED = None  # Auto-detect: tries pin 2, falls back to None if not available

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
DEFAULT_DUTY = 500
LOW_DUTY = 10
SLOW_BLINKING = 1
FAST_BLINKING = 3

# PWM_MAX_DUTY for legacy compatibility (used in calculations)
# Using machine.PWM directly with helper functions for gamma correction
PWM_MAX_DUTY = 1023  # Legacy scale reference (0..1023)
HIGH_DUTY = PWM_MAX_DUTY  # Full brightness reference

# END OF CONFIGURATION SECTION
# ================================


# Gamma correction for perceived brightness (human eye perceives brightness logarithmically)
# Common gamma values: 2.2 (sRGB standard), 2.8 (CIE luminance), 2.5 (good compromise)
GAMMA = 2.2  # Gamma correction factor
# Perceptible brightness range: skip the very dim range where LED is barely visible
MIN_PERCEPTIBLE_DUTY = 0.01  # 1% - below this the LED is basically off
MAX_PERCEPTIBLE_DUTY = 1.0  # 100% - full brightness


# --- Helper functions for PWM with gamma correction ---
def brightness_to_duty(brightness, use_perceptible_range=True):
    """
    Convert perceived brightness (0.0-1.0) to duty value (0-1023) with gamma correction.
    This makes brightness changes appear linear to the human eye.
    """
    if brightness <= 0:
        return 0
    brightness = min(1.0, float(brightness))

    if use_perceptible_range:
        # Map to perceptible range (skip very dim values)
        mapped = MIN_PERCEPTIBLE_DUTY + brightness * (
            MAX_PERCEPTIBLE_DUTY - MIN_PERCEPTIBLE_DUTY
        )
    else:
        mapped = brightness

    # Apply gamma correction
    duty_norm = mapped**GAMMA
    return int(round(duty_norm * 1023))


def set_led_freq(led, hz):
    """Set LED frequency, clamped to safe range."""
    hz = int(max(1, min(5000, hz)))
    led.freq(hz)


def set_led_duty(led, duty):
    """Set LED duty (0-1023)."""
    duty = int(max(0, min(1023, duty)))
    led.duty(duty)


# Using machine.PWM directly - no wrapper needed

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

# Initialize status LED with auto-detection for compatibility
# Works with both old ESP32 boards (with built-in LED on pin 2) and new ESP32-D boards (no built-in LED)
status_led = None
if STATUS_LED is False:
    # Explicitly disabled
    if DEBUG:
        print("Status LED explicitly disabled")
elif STATUS_LED is not None:
    # Explicitly configured pin
    try:
        status_led = machine.Pin(STATUS_LED, machine.Pin.OUT)
        if DEBUG:
            print(f"Status LED initialized on pin {STATUS_LED}")
    except Exception as e:
        if DEBUG:
            print(f"Warning: Could not initialize status LED on pin {STATUS_LED}: {e}")
        status_led = None
else:
    # Auto-detect: try pin 2 (common ESP32 built-in LED pin)
    try:
        test_pin = machine.Pin(2, machine.Pin.OUT)
        test_pin.on()
        time.sleep(0.1)
        test_pin.off()
        status_led = test_pin
        if DEBUG:
            print("Status LED auto-detected on pin 2")
    except Exception:
        # No built-in LED available (e.g., ESP32-D board)
        status_led = None
        if DEBUG:
            print("Status LED auto-detection: No built-in LED found (ESP32-D board?)")

leds = []
for led in LEDS:

    if SINGLE_LED_MODE or LED_STRIP_MODE:
        # PWM is used for these modes - use machine.PWM directly
        this_led = machine.PWM(machine.Pin(led))
        set_led_freq(this_led, DEFAULT_FREQ)
        set_led_duty(this_led, LOW_DUTY)  # Start at minimum brightness
        if DEBUG:
            print(
                f"PWM initialized on pin {led}: freq={this_led.freq()}, duty={this_led.duty()}/1023"
            )
        leds.append(this_led)
    else:
        # just standard connection is used for the other cases
        leds.append(machine.Pin(led, machine.Pin.OUT))

if LED_STRIP_MODE:
    for line in color_table:
        print(line)
        for i in range(3):
            # why is duty inversed? No idea about this, but it works that way
            duty_val = PWM_MAX_DUTY - line[i] * 2
            set_led_duty(leds[i], duty_val)
            set_led_freq(leds[i], 500)
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

    wlan = WifiManager(authmode=0)
    # makes the LED blink
    set_leds(freq=1)
    wlan.connect()  # ✅ Updated to use new Wi-Fi Manager
    # wlan = network.WLAN(network.STA_IF)
    # stop the blinking
    set_leds()

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
    my_headers = {"Range": "bytes=-2000"}

    try:
        response = urequests.get(
            "https://services.swpc.noaa.gov/json/goes/primary/xrays-6-hour.json",
            headers=my_headers,
            timeout=20,
        )
        text = response.text[:-1]
        response.close()
    except Exception:
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
        print("Response: ", text)

    # unfortunately, it is not fully deterministic when the high channel is at the correct position
    # to be extracted from the json. Therefore, we need to scan through the records in the response
    # to find the correct channel (i.e. 01-0.8nm)

    i = -1
    response_processed = text.split(", {")
    if DEBUG:
        print("\n Response processed: ", response_processed)

    while abs(i) < len(response_processed):

        return_value = 0.0
        try:
            #            response_processed = "{" + text.split(", {")[i]
            this_item = "{" + response_processed[i]
            if DEBUG:
                print("\n In loop: i, this item: ", i, this_item)

            response_json = ujson.loads(this_item)
            if response_json["energy"] == "0.1-0.8nm":
                return log(response_json["flux"]) - GOES_LIMIT

        except Exception:
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

        # TODO this has too many type conversions, color table should be
        # corrected to 0..PWM_MAX_DUTY and ints not strings
        duty_index = int(convert(val, GOES_B, GOES_M, 0, len(color_table) - 1))
        duty_rgb = color_table[duty_index]

        for i in range(3):
            # duty[i] = convert(int(duty_rgb[i]), 0, 255, 0, PWM_MAX_DUTY)
            duty[i] = int(convert(duty_rgb[i], 0.0, 1.0, 0, PWM_MAX_DUTY))

        if GOES_M < val < GOES_X:
            freq = [SLOW_BLINKING, SLOW_BLINKING, SLOW_BLINKING]
        elif val > GOES_X:
            freq = [FAST_BLINKING, FAST_BLINKING, FAST_BLINKING]

        if DEBUG:
            print("val, duty_index, duty_rgb, duty = ", val, duty_index, duty_rgb, duty)

    else:
        # Initialize with low duty (at minimum perceptible level)
        freq = DEFAULT_FREQ
        duty = LOW_DUTY

        if GOES_C < val < GOES_M:
            # Increase brightness from LOW to HIGH between GOES_C and GOES_M
            # Uses gamma correction for perceptually linear brightness change

            # Calculate perceived brightness (0.0 to 1.0) linearly based on GOES value
            perceived_brightness = (val - GOES_C) / (GOES_M - GOES_C)
            perceived_brightness = max(0.0, min(1.0, perceived_brightness))

            # Map to perceptible range (skip very dim values)
            if perceived_brightness > 0:
                mapped_brightness = MIN_PERCEPTIBLE_DUTY + perceived_brightness * (
                    MAX_PERCEPTIBLE_DUTY - MIN_PERCEPTIBLE_DUTY
                )
            else:
                mapped_brightness = 0

            # Apply gamma correction: duty = brightness ^ gamma
            if mapped_brightness > 0:
                gamma_corrected = mapped_brightness**GAMMA
            else:
                gamma_corrected = 0

            # Convert to duty value (0 to HIGH_DUTY)
            duty = int(gamma_corrected * HIGH_DUTY)
            duty = max(LOW_DUTY, min(HIGH_DUTY, duty))

        elif GOES_M < val < GOES_X:
            # Blink slowly - use 50% duty for visible blinking
            freq = SLOW_BLINKING
            duty = HIGH_DUTY // 2  # 50% duty for visible blinking

        elif val > GOES_X:
            # Blink fast - use 50% duty for visible blinking
            freq = FAST_BLINKING
            duty = HIGH_DUTY // 2  # 50% duty for visible blinking

    if DEBUG:
        print("freq, duty =", freq, duty)

    return freq, duty


# ---------
# Test function for goes_to_freq_duty


def test_goes_to_freq_duty(
    duration_per_step=0.5,
    start_val=None,
    end_val=None,
    sweep_duty_range=False,
    gamma_correct=False,
):
    """
    Test function for goes_to_freq_duty.
    Sweeps through the entire GOES value range and applies freq/duty to the LED.

    :param duration_per_step: Time in seconds to hold each value (default: 0.5)
    :param start_val: Starting GOES value (default: GOES_A - 1) or duty (0.0-1.0) if sweep_duty_range=True
    :param end_val: Ending GOES value (default: GOES_X + 2) or duty (0.0-1.0) if sweep_duty_range=True
    :param sweep_duty_range: If True, sweeps full duty range (0.0-1.0) instead of GOES values
    :param gamma_correct: If True (with sweep_duty_range), uses gamma correction for perceived brightness
    """
    print("\n" + "=" * 60)
    if sweep_duty_range:
        if gamma_correct:
            print(f"Testing PWM - Perceived Brightness Sweep (gamma={GAMMA})")
        else:
            print("Testing PWM - Full Duty Range Sweep (0.0 to 1.0)")
    else:
        print("Testing goes_to_freq_duty function - Full GOES Range Sweep")
    print("=" * 60)

    # Set default range if not provided
    if sweep_duty_range:
        # Sweep full duty range (0.0 to 1.0)
        if start_val is None:
            start_val = 0.0
        if end_val is None:
            end_val = 1.0
    else:
        # Sweep GOES values
        if start_val is None:
            start_val = GOES_A - 1
        if end_val is None:
            end_val = GOES_X + 2

    print("\n" + "=" * 60)
    print("PWM INFO:")
    print("=" * 60)
    print("  API: duty (0-1023)")
    if leds and len(leds) > 0:
        print(f"  Current: freq={leds[0].freq()} Hz, duty={leds[0].duty()}/1023")
    print("=" * 60)

    print("\nGOES thresholds:")
    print(f"  GOES_A = {GOES_A:.4f}")
    print(f"  GOES_B = {GOES_B:.4f}")
    print(f"  GOES_C = {GOES_C:.4f}")
    print(f"  GOES_M = {GOES_M:.4f}")
    print(f"  GOES_X = {GOES_X:.4f}")
    print("\nConstants:")
    print(f"  LOW_DUTY = {LOW_DUTY}")
    print(f"  HIGH_DUTY = {HIGH_DUTY}")
    print(f"  DEFAULT_FREQ = {DEFAULT_FREQ}")
    print(f"  SLOW_BLINKING = {SLOW_BLINKING}")
    print(f"  FAST_BLINKING = {FAST_BLINKING}")
    if sweep_duty_range:
        # Sweep full duty range (0.0 to 1.0) or perceived brightness
        if gamma_correct:
            print(
                f"\nBrightness range: {start_val:.3f} to {end_val:.3f} (perceived, gamma={GAMMA})"
            )
            print(
                f"Perceptible range: {MIN_PERCEPTIBLE_DUTY:.3f} to {MAX_PERCEPTIBLE_DUTY:.3f}"
            )
        else:
            print(f"\nDuty range: {start_val:.3f} to {end_val:.3f} (raw duty)")
        print(f"Step duration: {duration_per_step}s")
        print("\nStarting sweep...")
        print("-" * 60)
        if gamma_correct:
            print(f"{'Perceived':<12} {'Gamma Duty':<12} {'Raw Duty':<12} {'Freq':<8}")
        else:
            print(f"{'Duty Norm':<12} {'Raw Duty':<12} {'Freq':<8}")
        print("-" * 60)

        num_steps = 100  # 100 steps for smooth sweep
        step_size = (end_val - start_val) / num_steps

        current_val = start_val
        for i in range(num_steps + 1):
            current_val = max(0.0, min(1.0, current_val))

            set_led_freq(leds[0], DEFAULT_FREQ)

            if gamma_correct:
                # Use gamma-corrected brightness
                duty_raw = brightness_to_duty(current_val, use_perceptible_range=True)
            else:
                # Use raw duty
                duty_raw = int(round(current_val * 1023))

            set_led_duty(leds[0], duty_raw)
            actual_freq = leds[0].freq()

            if gamma_correct:
                print(f"{current_val:>11.3f}  {duty_raw:>11}  {actual_freq:<8}")
            else:
                print(f"{current_val:>11.3f}  {duty_raw:>11}  {actual_freq:<8}")

            time.sleep(duration_per_step)
            current_val += step_size
    else:
        # GOES value sweep with blinking tests
        blink_duration = 10  # seconds for each blinking test

        # Initialize LED to minimum brightness before starting
        print("\nInitializing LED to minimum brightness...")
        set_led_freq(leds[0], DEFAULT_FREQ)
        set_led_duty(leds[0], LOW_DUTY)
        time.sleep(0.5)

        # Phase 1: Brightness sweep from GOES_C to GOES_M
        print("\n--- Phase 1: Brightness sweep (GOES_C to GOES_M) ---")
        print(f"Test range: {GOES_C:.4f} to {GOES_M:.4f}")
        print(f"Step duration: {duration_per_step}s")
        print("-" * 70)
        print(f"{'Value':<12} {'Range':<20} {'Freq':<8} {'Duty':<8} {'Norm':<8}")
        print("-" * 70)

        num_steps = int((GOES_M - GOES_C) * 10)
        if num_steps < 10:
            num_steps = 10
        step_size = (GOES_M - GOES_C) / num_steps

        current_val = GOES_C
        for i in range(num_steps + 1):
            freq, duty = goes_to_freq_duty(current_val, rgb=False)

            set_led_freq(leds[0], freq)
            set_led_duty(leds[0], duty)
            duty_norm = duty / float(HIGH_DUTY) if HIGH_DUTY > 0 else 0.0

            range_name = "GOES_C to GOES_M"
            print(
                f"{current_val:>11.4f}  {range_name:<20} {freq:<8} {duty:<8} {duty_norm:.3f}"
            )

            time.sleep(duration_per_step)
            current_val += step_size

        # Phase 2: Slow blinking (GOES_M to GOES_X)
        print("-" * 70)
        print("\n--- Phase 2: Slow blinking (GOES_M to GOES_X) ---")
        print(f"Frequency: {SLOW_BLINKING} Hz, Duty: {HIGH_DUTY // 2} (50%)")
        print(f"Blinking for {blink_duration} seconds...")

        test_val = (GOES_M + GOES_X) / 2  # Midpoint
        freq, duty = goes_to_freq_duty(test_val, rgb=False)

        set_led_freq(leds[0], freq)
        set_led_duty(leds[0], duty)

        print(f"  Value: {test_val:.4f}, Freq: {freq}, Duty: {duty}")
        time.sleep(blink_duration)

        # Phase 3: Fast blinking (above GOES_X)
        print("-" * 70)
        print("\n--- Phase 3: Fast blinking (above GOES_X) ---")
        print(f"Frequency: {FAST_BLINKING} Hz, Duty: {HIGH_DUTY // 2} (50%)")
        print(f"Blinking for {blink_duration} seconds...")

        test_val = GOES_X + 1  # Above GOES_X
        freq, duty = goes_to_freq_duty(test_val, rgb=False)

        set_led_freq(leds[0], freq)
        set_led_duty(leds[0], duty)

        print(f"  Value: {test_val:.4f}, Freq: {freq}, Duty: {duty}")
        time.sleep(blink_duration)

    print("-" * 70)
    print("\nTest complete! Turning off LED...")
    set_led_freq(leds[0], DEFAULT_FREQ)
    set_led_duty(leds[0], 0)
    print("=" * 60 + "\n")


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
        if DEBUG:
            print("value entered = ", val)

        range = abs(input_range[1] - input_range[0])

        if range > 0:
            slope = float(nb_LED) / (range)
        else:
            slope = 0

        # val = min(max(ceil(log(float(val), 10)+7), 0), numLEDs)
        # val = int(round( np.interp( val, input_range, [0,nb_LED-1])))
        val = int(round(slope / val + 1))

        if DEBUG:
            print("range, solpe, val = ", range, slope, val)

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
            set_led_freq(leds[0], freq)
            set_led_duty(leds[0], duty)
            return

        for led in leds:
            led.duty(0)  # off
        if val >= 0:
            for led in leds[:val]:
                led.duty(1023)  # on
        else:
            leds[-1].duty(1023)  # on

    else:
        print(freq, duty)
        for i in range(3):
            set_led_freq(leds[i], freq[i])
            set_led_duty(leds[i], duty[i])


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

            for i in range(3):
                set_led_freq(leds[i], 500)
            for color in color_table:
                for i in range(3):
                    this_duty = int(convert(int(color[i]), 0, 255, 0, PWM_MAX_DUTY))
                    set_led_duty(leds[i], this_duty)
                    if DEBUG:
                        print(
                            "color, duty, leds[i] =  ",
                            color[i],
                            this_duty,
                            leds[0].duty(),
                            leds[1].duty(),
                            leds[2].duty(),
                        )
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
    print("LED vals: ", lp)


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

        if status_led is not None:
            status_led.on()

        # current_goes_val = get_current_goes_val(log_scale=not FLARE_MODE and not LED_STRIP_MODE)
        current_goes_val = get_current_goes_val()  # always in log scale
        if DEBUG:
            print("\n current GOES value: ", current_goes_val)

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
                level = goes_to_int(
                    current_goes_val,
                    input_range=[min([i for i in diff if i > 0]), max(diff)],
                )

                if DEBUG:
                    print("\n Level: ", level)
                # led_no = val_str2int(val, len(leds))

                set_leds(level)

        else:
            if DEBUG:
                print("\n No correct GOES val returned, skip this time")

        if status_led is not None:
            status_led.off()

        if DEBUG:
            print(current_goes_val)
        # TODO repair this
        #         print_led_vals()

        time.sleep(60)


# Only run main automatically if RUN is True
# Set RUN = False before importing to prevent auto-start (for testing)
# Uncomment the lines below to enable auto-start when imported
# if RUN:
#     try:
#         _main()
#     except KeyboardInterrupt:
#         print("Main program interrupted")
