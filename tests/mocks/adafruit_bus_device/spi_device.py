
class SPIDevice(object):
    def __init__(self, spidev, *a, **kw):
        self.spidev = spidev

        self.data = b''

        self.no_writes = False

    def write(self, b):
        if self.no_writes:
            return
        self.data = b

    def readinto(self, b):
        for i, c in enumerate(self.data):
            b[i] = c

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        pass
