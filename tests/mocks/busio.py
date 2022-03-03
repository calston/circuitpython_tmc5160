class SPI(object):
    def __init__(self, clk, MOSI=None, MISO=None):
        self.clk = clk
        self.MOSI = MOSI
        self.MISO = MISO
