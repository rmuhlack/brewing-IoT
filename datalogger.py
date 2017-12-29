import time
import yaml
import sys
import RPi.GPIO as GPIO
import logging
import Adafruit_GPIO

from hx711 import HX711
from Adafruit_MAX31856 import MAX31856 as MAX31856

def validate_config(c):

    if not c.has_key('pi-indicator-config'):
        print "Configuration error: Configuration must contain a pi-indicator-config section"
        sys.exit(1)

    if not c['pi-indicator-config'].has_key('sources'):
        print "Configuration error: no sources defined"
        sys.exit(1)

    return

def post_data(delta,T1,T2):
    print "Delta CO2 (g):{0:0.0F}  Ferment Temp (C): {0:0.3F}  Internal Temp (C): {0:0.3F}".format(delta,T1,T2)

def cleanAndExit():
    print ('Cleaning...')
    GPIO.cleanup()
    print ('Bye!')
    sys.exit()

######
# main program
# load config
with open("config.yml", 'r') as stream:
    try:
        config = yaml.load(stream)
    except yaml.YAMLError as exc:
        print exc
        sys.exit(1)

validate_config(config)
config = config['brewing-config']

hx = HX711(5, 6)
hx.set_reading_format("LSB", "MSB")
hx.set_reference_unit(-22.535)

hx.reset()
hx.tare()

## Raspberry Pi software SPI configuration.
software_spi = {"clk": 14, "cs": 10, "do": 13, "di": 12}
sensor = MAX31856(software_spi=software_spi)

# loop and collect/log data
try:
    while True:
        deltaCO2 = hx.get_weight(5)
        ferment_temp = sensor.read_temp_c()
        internal_temp = sensor.read_internal_temp_c()
        post_data(deltaCO2,ferment_temp,internal_temp)

        time.sleep(1)
except (KeyboardInterrupt):
    sys.exit(0)