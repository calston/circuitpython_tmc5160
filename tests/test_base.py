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

def test_global_config(motor: TMC5160):
    motor.setGlobalConfig()
    assert motor.tmcdev.data == bytes([0x80, 0, 0, 0, 0])

    motor.setGlobalConfig(enable_pwm=True, multistep_filter=True)
    assert motor.tmcdev.data == bytes([0x80, 0, 0, 0, 0x0C])

def test_chopper_config(motor: TMC5160):
    motor.setChopperConfig(off_time=3, hysteresis_start=4, hysteresis_low=1, blank_time=2)

    assert motor.tmcdev.data == bytes([0x6c | 0x80, 0, 0x01, 0, 0xC3])

def test_pwm_config(motor: TMC5160):
    motor.setPwmConfig(pwm_limit=False, pwm_regulation=0, pwm_offset=200,
                       pwm_autogradient=False, pwm_gradient=1, pwm_autoscale=1)

    assert motor.tmcdev.data == bytes([0x70 | 0x80, 0, 0x04, 0x01, 0xC8])

def test_very_large_int(motor: TMC5160):
    motor.writeint(1, 0xFFFFFFFFFFFFFF)

    assert motor.tmcdev.data == bytes([0x81, 0xFF, 0xFF, 0xFF, 0xFF])
    
    motor.writeint(1, 0xFFFFFFFFFFBEEF)

    assert motor.tmcdev.data == bytes([0x81, 0xFF, 0xFF, 0xBE, 0xEF])
    
def test_negative_int(motor: TMC5160):
    motor.writeint(1, -9999, signed=True)

    motor.tmcdev.no_writes = True
    
    val = motor.readint(1, signed=True)

    assert val == -9999

def test_positive_signed_int(motor: TMC5160):
    motor.writeint(1, 9999, signed=True)

    motor.tmcdev.no_writes = True
    
    val = motor.readint(1, signed=True)

    assert val == 9999    

def test_readint(motor: TMC5160):
    motor.writeint(1, 1234)
    motor.tmcdev.no_writes = True
    
    val = motor.readint(1)
    assert val == 1234
