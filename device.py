import uuid
import numpy

class GyroscopeEvent():
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class AccelerometerEvent():
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class Device():
    def __init__(self, identifier):
        self.identifier = identifier

        # angles used to normalize acceleration and gyro
        # self.normalize = (0, 0, 0)

        # all callbacks defined in these handlers will be called on change
        self.gyroscope_handlers = []
        self.acceleration_handlers = []
        self.normalize_handlers = []

    @staticmethod
    def scan():
        """scan for nearby devices and return a list of identifiers."""
        pass

    @staticmethod
    def connect(identifier):
        """connect a device"""
        pass

    def listen():
        """start listening on the device and propagate events"""

    def normalize(self):
        """calculate the rotational matrix that normalize acceleration and gyro data"""
        x, y, z = self.gyroscope()

    def acceleration(self, coordinate=None):
        """query the accelerometer"""
        pass

    def gyroscope(self, coordinate=None):
        """query the gyroscope"""
        pass

from pymouse import PyMouse, PyMouseEvent
from threading import Thread

class MouseDevice(Device):
    mouse = PyMouse()

    @staticmethod
    def scan():
        return [MouseDevice(uuid.uuid4().hex)]

    def normalize(self):
        print('mouse is normalized at {} {}'.format(*self.mouse.position()))
        self.initial_position = self.mouse.position()

    def listen(self):

        device = self

        class ClickListener(PyMouseEvent):
            def click(self, x, y, button, press):
                print('clicked {} {} {} {}'.format(x, y, button, press))

            def move(self, x, y):
                x, y = x - device.initial_position[0], y - device.initial_position[0]
                print('new coordinates {} {}'.format(x, y))

        c = ClickListener()
        thread = Thread()
        thread.run = c.run

        thread.start()

from Xlib import X, display

class KeyboardDevice(Device):
    display = display.Display()

    @staticmethod
    def scan():
        return [KeyboardDevice(uuid.uuid4().hex)]

    def normalize():
        # already normalized
        pass

    def listen(self):
        pass

import bluetooth

class BluetoothDevice(Device):
    @staticmethod
    def scan():
        return [BluetoothDevice(device) for device in bluetooth.discover_devices()]

    def connect(self):
        pass


if __name__ == '__main__':
    mouse = MouseDevice('test')
    mouse.normalize()
    mouse.listen()
