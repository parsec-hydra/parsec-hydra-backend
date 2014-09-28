#!/usr/bin/env python2

from flask import Flask, jsonify, g, abort
from flask.ext.socketio import SocketIO, send
import flask.ext.socketio as socketio

import numpy
import time
import uuid
import subprocess
import re
import struct
import threading

from bluepy.bluepy.btle import Peripheral, Service, BTLEException

app = Flask(__name__)
app.config['SECRET_KEY'] = uuid.uuid4().hex
socketio = SocketIO(app)

NOD_SERVICE_MOTION6D_TYPE='net.openspatial.characteristic.pose6d'
NOD_SERVICE_MOTION6D_UUID='00000205-0000-1000-8000-a0e5e9-000000'

subprocess.call(['killall', '-9', 'gatttool'])
subprocess.call(['killall', '-9', 'bluepy-helper'])

@app.before_request
def check_device():
    if not 'peripheral' in app.config:
        app.logger.info('Pairing the device...')
        app.config['peripheral'] = Peripheral('A0:E5:E9:00:01:F2')
        app.logger.info('Paired the device!')

        app.logger.info('Discovering services...')
        services = app.config['peripheral'].discoverServices()
        app.logger.info('Discovered services:', services)

        # register the motion6d service
        # motion6Dservice = Service(app.config['peripheral'], NOD_SERVICE_MOTION6D_UUID, 1, 10)
        # app.logger.info(''.join(motion6Dservice.getCharacteristics()))

@app.route('/')
def home():
    """ping the web application"""
    return 'Hello world sent at ' + str(time.time())

@app.route('/<device>/services')
def services(device):
    """list services available on the device"""
    return jsonify({str(service.uuid): str(service) for service in app.config['peripheral'].getServices()})

@app.route('/<device>/characteristics')
def characteristics(device):
    """list all device characteristics"""
    characteristics = {}

    for service in app.config['peripheral'].getServices():
        if not str(service.uuid) in characteristics:
            characteristics[str(service.uuid)] = {}
        for characteristic in service.getCharacteristics():
            try:
                characteristics[str(service.uuid)][str(characteristic.uuid)] = characteristic.read().encode('hex')
            except BTLEException as e:
                characteristics[str(service.uuid)][str(characteristic.uuid)] = repr(e)
                app.logger.error(e)
    return jsonify(characteristics)

@app.route('/<device>/<service>/characteristics')
def service_characteristics(device, service):
    """list characteristics for a given service"""
    service = app.config['peripheral'].getServiceByUUID(service)
    characteristics = {}

    for characteristic in service.getCharacteristics():
        try:
            characteristics[str(characteristic.uuid)] = characteristic.read().encode('hex')
        except BTLEException as e:
            characteristics[str(characteristic.uuid)] = repr(e)
            app.logger.error(e)

    return jsonify(characteristics)

@app.route('/<device>/<service>/<characteristic>/read')
def read(device, service, characteristic):
    """read data corresponding to a given characteristic"""
    return app.config['peripheral'].getServiceByUUID(service).getCharacteristics(characteristic)[0].read().encode('hex')

@app.route('/<device>/<service>/<characteristic>/notify')
def notify(device, service, characteristic):
    """enable notify mode for a given characteristic"""

    # disconnect the peripheral
    app.config['peripheral'].disconnect()

    def _run():
        child = subprocess.Popen(['./gatttool', '--device=' + device, '--adapter=hci0', '--interactive'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, universal_newlines=True)     

        # enable notifications :)
        child.stdin.write("connect\n")
        child.stdin.flush()

        # wait until the connection is successful
        time.sleep(2)

        # enable notifications
        child.stdin.write("char-write-req 0x004c 0100\n")
        child.stdin.flush()

        matcher = re.compile('Notification handle = 0x004b value: ([0-9a-f ]+)')

        while child.poll() is None:
            groups = matcher.search(child.stdout.readline())
            if groups:
                b = groups.group(1).replace(' ', '')
                yaw, pitch, roll, z, y, x = tuple(struct.unpack(">H", b[i:i+2])[0] for i in range(12, len(b), 2))
                app.logger.info('{} becomes {}, {}, {}, {}, {}, {}'.format(b, x, y, z, roll, pitch, yaw))
                
                socketio.send('{};{};{};{};{};{}'.format(x, y, z, roll, pitch, yaw))

    # threading this code..
    t = threading.Thread()
    t.run = _run
    t.start()

    return 'notified'

@app.route('/<device>/<service>/<characteristic>/unnotify')
def unnotify():
    """disable notify to stop insanity"""
    pass

# WebSocket communication
@socketio.on('connect')
def connect(data):
    app.logger.info('%s has connected', data)
    emit('yo', {'data': 'Connected'})

@socketio.on('disconnect')
def disconnect(data):
    app.logger.info('%s has disconnected.', data)

@socketio.on('message')
def message():
    app.logger.info('Received a message containing: %s', data)

if __name__ == '__main__':
    app.debug = True
    socketio.run(app, host='0.0.0.0')
