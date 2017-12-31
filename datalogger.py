#!/usr/bin/python

import time
import yaml
import sys
import logging

import argparse
import datetime
from time import gmtime, strftime
import subprocess

import jwt
import paho.mqtt.client as mqtt

def create_jwt(project_id, private_key_file, algorithm):
    """Creates a JWT (https://jwt.io) to establish an MQTT connection.
    Args:
     project_id: The cloud project ID this device belongs to
     private_key_file: A path to a file containing either an RSA256 or ES256
         private key.
     algorithm: The encryption algorithm to use. Either 'RS256' or 'ES256'
    Returns:
      An MQTT generated from the given project_id and private key, which
      expires in 20 minutes. After 20 minutes, your client will be
      disconnected, and a new JWT will have to be generated.
    Raises:
      ValueError: If the private_key_file does not contain a known key.
    """

    token = {
        # The time that the token was issued at
        'iat': datetime.datetime.utcnow(),
        # When this token expires. The device will be disconnected after the
        # token expires, and will have to reconnect.
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
        # The audience field should always be set to the GCP project id.
        'aud': project_id
    }

    # Read the private key file.
    with open(private_key_file, 'r') as f:
        private_key = f.read()

    print(
            'Creating JWT using {} from private key file {}'.format(
                    algorithm, private_key_file))

    return jwt.encode(token, private_key, algorithm=algorithm)

def error_str(rc):
    """Convert a Paho error to a human readable string."""
    return '{}: {}'.format(rc, mqtt.error_string(rc))


def on_connect(unused_client, unused_userdata, unused_flags, rc):
    """Callback for when a device connects."""
    print('on_connect', error_str(rc))


def on_disconnect(unused_client, unused_userdata, rc):
    """Paho callback for when a device disconnects."""
    print('on_disconnect', error_str(rc))


def on_publish(unused_client, unused_userdata, unused_mid):
    """Paho callback when a message is sent to the broker."""
    print('on_publish')


def validate_config(c):

    # if not c.has_key('pi-indicator-config'):
    #     print "Configuration error: Configuration must contain a pi-indicator-config section"
    #     sys.exit(1)

    # if not c['pi-indicator-config'].has_key('sources'):
    #     print "Configuration error: no sources defined"
    #     sys.exit(1)

    return

def cleanAndExit():
    print ('Cleaning...')
    GPIO.cleanup()
    print ('Bye!')
    sys.exit()


def parse_command_line_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description=(
                'Brewery IoT Sensors Client'))
    parser.add_argument(
            '--config',
            default='config.yml',
            help='Brewery IoT Configuration Filename')
    parser.add_argument(
            '--device_id',
            default='',
            help='IoT Core device id - overrides any provided by config file')
    parser.add_argument(
            '--stubhw',
            default='FALSE',
            help='Stub hardware for testing')

    return parser.parse_args()

def mqtt_initialise(config):
    # Create our MQTT client. The client_id is a unique string that identifies
    # this device. For Google Cloud IoT Core, it must be in the format below.
    global client
    global mqtt_config
    mqtt_config = config

    client = mqtt.Client(
            client_id=(
                    'projects/{}/locations/{}/registries/{}/devices/{}'
                    .format(
                            config['project_id'], config['cloud_region'],
                            config['registry_id'], config['device_id'])))

    # With Google Cloud IoT Core, the username field is ignored, and the
    # password field is used to transmit a JWT to authorize the device.
    client.username_pw_set(
            username='unused',
            password=create_jwt(
                    config['project_id'], config['private_key_file'], config['algorithm']))

    # Enable SSL/TLS support.
    client.tls_set(ca_certs=config['ca_certs'])

    # Register message callbacks. https://eclipse.org/paho/clients/python/docs/
    # describes additional callbacks that Paho supports. In this example, the
    # callbacks just print to standard out.
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.on_disconnect = on_disconnect

    # Connect to the Google MQTT bridge.
    client.connect(config['mqtt_bridge_hostname'], config['mqtt_bridge_port'])

    # Start the network loop.
    client.loop_start()

    mqtt_config['topic'] = '/devices/{}/events'.format(config['device_id'])
    
    return

def mqtt_publish_update(delta, T1, T2):
    global client
    global mqtt_config
    print(mqtt_config)
    payload = '{{ "device_id": "{}", "timestamp": "{}", "delta_weight": "{:0.0F}", "fermenter_temp": "{:0.3F}", "internal_temp": "{:0.3F}" }}'.format(
            mqtt_config['device_id'],
            strftime("%Y-%m-%d %H:%M:%S", gmtime()),
            delta,
            T1,
            T2)

    print(
            'Publishing message {}'.format(payload))
    # Publish "payload" to the MQTT topic. qos=1 means at least once
    # delivery. Cloud IoT Core also supports qos=0 for at most once
    # delivery.
    client.publish(mqtt_config['topic'], payload, qos=1)

    return

def mqtt_cleanup():
    # End the network loop and finish.
    global client
    client.loop_stop()
    print('MQTT Finished.')

    return

def getRandom():
    return 10


######
# main program
# load config
def main():
    args = parse_command_line_args()

    with open(args.config, 'r') as stream:
        try:
            config = yaml.load(stream)
        except yaml.YAMLError as exc:
            print (exc)
            sys.exit(1)

    validate_config(config)
    config = config['brewing-config']

    # setup sensors
    if (args.stubhw == "FALSE"):
        import sources.scales
        import sources.thermometer

        sources.scales.initialise(config['hx711'])
        getWeightDelta = sources.scales.getWeightDelta

        sources.thermometer.initialise(config['MAX31856'])
        getProbeTemperature = sources.thermometer.getProbeTemperature
        getInternalTemperature = sources.thermometer.getInternalTemperature

    else:
        getWeightDelta = getRandom
        getProbeTemperature = getRandom
        getInternalTemperature = getRandom


    # connect to IoT core
    mqtt_initialise(config['google-iot'])

    # loop and collect/log data
    try:
        while True:
            deltaCO2 = getWeightDelta()
            ferment_temp = getProbeTemperature()
            internal_temp = getInternalTemperature()
            mqtt_publish_update(deltaCO2,ferment_temp,internal_temp)

            time.sleep(1)
    except (KeyboardInterrupt):
        sys.exit(0)

if __name__ == '__main__':
    main()

