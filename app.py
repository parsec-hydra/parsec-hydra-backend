from flask import Flask, jsonify, g
from flask.ext.socketio import SocketIO, emit
import numpy
import time

from device import KeyboardDevice, BluetoothDevice, MouseDevice

from os import environ

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(app)

@app.route('/<device>(/<coordinate>)')
def acceleration(device, coordinate = None):
    pass

@app.route('/ping')
def ping():
    """ping the web application"""
    return 'Hello world sent at ' + str(time.time())

@app.before_first_request
def initialize_devices():
    g.devices = []

@app.route('/devices')
@app.route('/devices/<state>')
def devices(state=None):
    """list devices available"""
    devices = []

    if state == 'connected':
        return jsonify(g.devices)

    providers = {KeyboardDevice, BluetoothDevice, MouseDevice}

    for provider in providers:
        devices.extend(provider.scan())

    return jsonify({d.identifier: str(d) for d in devices})

@app.route('/<device>/connect')
def connect(device):
    """connect a given device"""
    g.device = device

@app.route('/<device>(/<coordinate>)')
def listen(device):
    pass

@socketio.on('ping')
def ping_websocket():
    """ping the websocket"""
    emit('Hello world sent at ' + str(time.time()))

@socketio.on('connect')
def test_connect():
    app.logger.info('%s has connected', )
    emit('yo', {'data': 'Connected'})

if __name__ == '__main__':
    #app.run(host='0.0.0.0', debug=True)
    app.debug = True
    socketio.run(app, host='0.0.0.0')
