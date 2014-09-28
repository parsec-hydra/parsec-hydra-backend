from flask import Flask, jsonify, g
from flask.ext.socketio import SocketIO, emit
import numpy
import time
import uuid
import json

from bluepy.bluepy.btle import Peripheral, Service

app = Flask(__name__)
app.config['SECRET_KEY'] = uuid.uuid4().hex
socketio = SocketIO(app)

NOD_SERVICE_MOTION6D_UUID='00000205-0000-1000-8000-a0e5e9-000000'

@app.before_first_request
def initialize_devices():
    """make sure devices dict is initialized"""
    app.logger.info('Pairing the device...')
    g.peripheral = Peripheral('A0:E5:E9:00:01:F2')
    app.logger.info('Paired the device!')

    # register the motion6d service
    motion6Dservice = Service(g.peripheral, NOD_SERVICE_MOTION6D_UUID, 1, 10)
    app.logger.info(''.join(motion6Dservice.getCharacteristics()))

@app.route('/')
def ping():
    """ping the web application"""
    return 'Hello world sent at ' + str(time.time())

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
