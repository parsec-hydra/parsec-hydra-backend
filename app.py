#!/usr/bin/env python2

from flask import Flask, jsonify, g, abort, render_template
from flask.ext.socketio import SocketIO, send
import flask.ext.socketio as socketio

import numpy
import time
import uuid
import subprocess
import re
import struct
import threading
import json

from bluepy.bluepy.btle import Peripheral, Service, BTLEException

app = Flask(__name__)
app.config['SECRET_KEY'] = uuid.uuid4().hex
app.config['devices'] = {} # device are mapped uuid => Peripheral
socketio = SocketIO(app)

NOD_SERVICE_MOTION6D_TYPE='net.openspatial.characteristic.pose6d'
NOD_SERVICE_MOTION6D_UUID='00000205-0000-1000-8000-a0e5e9-000000'

# kill annoying processes
subprocess.call(['killall', '-9', 'gatttool'])
subprocess.call(['killall', '-9', 'bluepy-helper'])

@app.before_request
def check_device():
    """connect the device if it's not paired"""
    if not 'peripheral' in app.config:
        try:
            app.logger.info('Pairing the device...')
            app.config['peripheral'] = Peripheral('A0:E5:E9:00:01:F2')
            app.logger.info('Paired the device!')

            app.logger.info('Discovering services...')
            services = app.config['peripheral'].discoverServices()
            app.logger.info('Discovered services:', services)
        except BTLEException as b:
            app.logger.error(b)
            abort(503)

@app.route('/')
def ping():
    """ping the web application"""
    return render_template('ping.html', time=time.time())

@app.route('/<device>/services')
def services(device):
    """list services available on the device"""
    return render_template('services.html', services=app.config['peripheral'].getServices())
    # return jsonify({str(service.uuid): str(service) for service in app.config['peripheral'].getServices()})

@app.route('/<device>/characteristics')
def characteristics(device):
    """list all device characteristics"""
    characteristics = {}

    for service in app.config['peripheral'].getServices():
        if not service.uuid in characteristics:
            characteristics[service.uuid] = {}
        for characteristic in service.getCharacteristics():
            try:
                characteristics[service.uuid][characteristic.uuid] = characteristic.read().encode('hex')
            except BTLEException as e:
                characteristics[service.uuid][characteristic.uuid] = repr(e)
                app.logger.error(e)

    return render_template('characteristics.html', characteristics=characteristics)

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
                
                socketio.send(json.dumps([x, y, z, roll, pitch, yaw]), True);

                time.sleep(0.01)

    # threading this code..
    t = threading.Thread()
    t.daemon = True
    t.run = _run
    t.start()

    return render_template('notify.html')

@app.route('/<device>/<service>/<characteristic>/unnotify')
def unnotify():
    """disable notify to stop insanity"""
    pass

@app.route('/message/<data>')
def message(data):
    socketio.send(data)
    return 'Just sent ' + data

# WebSocket communication
@socketio.on('connect')
def connect(data):
    app.logger.info('%s has connected', data)
    emit('yo', {'data': 'Connected'})

@socketio.on('disconnect')
def disconnect():
    app.logger.info('%s has disconnected.')

@socketio.on('message')
def message(data):
    app.logger.info('Received a message containing: %s', data)

if __name__ == '__main__':
    app.debug = True
    # app.run(host='0.0.0.0', debug=True)
    socketio.run(app, host='0.0.0.0')
