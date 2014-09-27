from flask import Flask, jsonify, g
from flask.ext.socketio import SocketIO, emit
import numpy
import time

from device import KeyboardDevice, BluetoothDevice

from os import environ

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(app)

@app.route('/<device>(/<coordinate>)')
def acceleration(device, coordinate = None):
    pass

@app.route('/ping')
def ping():
    return 'Hello world sent at ' + str(time.time())

@app.route('/devices')
def devices():
    return jsonify({d.identifier: str(d) for d in KeyboardDevice.scan()})

@app.route('/<device>(/<coordinate>)')
def listen(device):
    pass

@app.route('/<device>/connect')
def connect(device):
    g.devices.append(device)

@socketio.on('connect')
def test_connect():
    emit('yo', {'data': 'Connected'})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')
