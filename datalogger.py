import time
import yaml
import sys
import logging
import sources.scales
import sources.thermometer

def validate_config(c):

    # if not c.has_key('pi-indicator-config'):
    #     print "Configuration error: Configuration must contain a pi-indicator-config section"
    #     sys.exit(1)

    # if not c['pi-indicator-config'].has_key('sources'):
    #     print "Configuration error: no sources defined"
    #     sys.exit(1)

    return

def post_data(delta,T1,T2):
    print "Delta CO2 (g):{:0.0F}  Ferment Temp (C): {:0.3F}  Internal Temp (C): {:0.3F}".format(delta,T1,T2)

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

# setup sensors
sources.scales.initialise(config['hx711'])
sources.thermometer.initialise(config['MAX31856'])

# loop and collect/log data
try:
    while True:
        deltaCO2 = sources.scales.getWeightDelta()
        ferment_temp = sources.thermometer.getProbeTemperature()
        internal_temp = sources.thermometer.getInternalTemperature()
        post_data(deltaCO2,ferment_temp,internal_temp)

        time.sleep(1)
except (KeyboardInterrupt):
    sys.exit(0)
