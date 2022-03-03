import sys

class Pin(object):
    def __init__(self, num):
        self.num = num

class This(object):
    def __getattr__(self, *a):
        if a[0].startswith('GP'):
            return Pin(int(a[0].lstrip('GP')))

sys.modules[__name__] = This()
