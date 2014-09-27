from flask import Flask, jsonify
import numpy
import time

app = Flask(__name__)

@app.route('/<device>(/<coordinate>)')
def acceleration(device, coordinate = None):
    pass

@app.route('/ping')
def ping():
    return 'Hello world sent at ' + str(time.time())

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
