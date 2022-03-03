
class SPIDevice(object):
    def __init__(self, spidev, *a, **kw):
        self.spidev = spidev

        self.data = b''

    def write(self, b):
        self.data = b

    def readinto(self, b):
        b = self.data

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        pass
