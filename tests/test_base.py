import sys
import os
import pytest

# Fake CircuitPython modules for standalone testing
test_dir = os.path.join(os.path.dirname(__file__), 'mocks')
sys.path.append(test_dir)

from tmc5160 import TMC5160
import board

@pytest.fixture
def motor():
    return TMC5160(board.GP1, board.GP2, board.GP3, board.GP4, board.GP5)

def test_global_config(motor):
    motor.setGlobalConfig()

    assert motor.tmcdev.data == bytes([0x80, 0, 0, 0, 0x60])

def test_chopper_config(motor):
    motor.setChopperConfig(off_time=3, hysteresis_start=4, hysteresis_low=1, blank_time=2)

    assert motor.tmcdev.data == bytes([0x6c | 0x80, 0, 0x01, 0, 0xC3])