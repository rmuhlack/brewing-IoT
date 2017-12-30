import RPi.GPIO as GPIO
import time
import sys
from hx711 import HX711



def initialise(config):
    """Initialise load cells hardware and tare"""
    # config parameters should be available as config['??']
    global __hx__
    __hx__ = HX711(5, 6)

    # HOW TO CALCULATE THE REFFERENCE UNIT
    # To set the reference unit to 1. Put 1kg on your sensor or anything you have and know exactly how much it weights.
    # In this case, 92 is 1 gram because, with 1 as a reference unit I got numbers near 0 without any weight
    # and I got numbers around 184000 when I added 2kg. So, according to the rule of thirds:
    # If 2000 grams is 184000 then 1000 grams is 184000 / 2000 = 92.
    #hx.set_reference_unit(113)
    __hx__.set_reference_unit(-22.535)

    # I've found out that, for some reason, the order of the bytes is not always the same between versions of python, numpy and the hx711 itself.
    # Still need to figure out why does it change.
    # If you're experiencing super random values, change these values to MSB or LSB until to get more stable values.
    # There is some code below to debug and log the order of the bits and the bytes.
    # The first parameter is the order in which the bytes are used to build the "long" value.
    # The second paramter is the order of the bits inside each byte.
    # According to the HX711 Datasheet, the second parameter is MSB so you shouldn't need to modify it.
    __hx__.set_reading_format("LSB", "MSB")

    __hx__.reset()
    __hx__.tare()


def cleanup():
    GPIO.cleanup()


def getWeightDelta():
    # the HX711 author reports that if the sensor has been asleep for some time it is best to reset prior
    global __hx__

    __hx__.reset()
    val = hx.get_weight(5)

    # power down in case we are trying to be power conscious
    __hx__.power_down()

    return val

if __name__ == "__main__":
    import sys
    print ("Should have a test harness here")

