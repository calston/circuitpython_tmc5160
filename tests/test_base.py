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
