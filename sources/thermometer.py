import time
import Adafruit_GPIO

# Local Imports
from Adafruit_MAX31856 import MAX31856 as MAX31856


def initialise(config):
    """Initialise thermocouple hardware"""
    global __sensor__

    software_spi = {"clk": 11, "cs": 22, "do": 9, "di": 10}
    __sensor__ = MAX31856(software_spi=software_spi)

    return

def cleanup():
    # no known clean up tasks for teh MAX31856 or Adafruit_GPIO?
    return

def getProbeTemperature():
    global __sensor__

    return __sensor__.read_temp_c()

def getInternalTemperature():
    global __sensor__

    return __sensor__.read_internal_temp_c()


if __name__ == "__main__":
    import sys
    print ("Should have a test harness here")
