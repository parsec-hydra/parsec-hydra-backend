from flask import Flask, jsonify, g, abort
from flask.ext.socketio import SocketIO, emit
import numpy
import time
import uuid

from bluepy.bluepy.btle import Peripheral, Service, BTLEException

app = Flask(__name__)
app.config['SECRET_KEY'] = uuid.uuid4().hex
socketio = SocketIO(app)

NOD_SERVICE_MOTION6D_TYPE='net.openspatial.characteristic.pose6d'
NOD_SERVICE_MOTION6D_UUID='00000205-0000-1000-8000-a0e5e9-000000'

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
def notify(service, characteristic):
    """enable notify mode for a given characteristic"""
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
    app.run(host='0.0.0.0', debug=True)
    #socketio.run(app, host='0.0.0.0')
