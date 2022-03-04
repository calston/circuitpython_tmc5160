import board
import busio
import time

from adafruit_bus_device.spi_device import SPIDevice
from digitalio import DigitalInOut

from .tmcreg import *

class TMC5160(object):
    def __init__(self, clk, mosi, miso, cs, en, sd_mode=None, baud=1000000, max_i=2.2, standalone=False) -> None:
        tmc_spi = busio.SPI(clk, MOSI=mosi, MISO=miso)
        tmc_cs = DigitalInOut(cs)
        self.tmcdev = SPIDevice(tmc_spi, tmc_cs, baudrate=baud, polarity=0, phase=0)

        self.tmc_en = DigitalInOut(en)
        self.tmc_en.switch_to_output()
        self.tmc_en.value = 1

        # Used to calculate output current
        self.max_i = 2.2

        if sd_mode:
            self.tmc_mode = DigitalInOut(sd_mode)
            self.tmc_mode.switch_to_output()
            self.tmc_mode.value = 0

        else:
            self.tmc_mode = None

        # Standalone mode
        self.standalone = standalone

    def write(self, address, *b):
        with self.tmcdev as spi:
            spi.write(bytes([address | 0x80, b[0], b[1], b[2], b[3]]))

    def writeint(self, address, value):
        self.write(
            address | 0x80,
            0xff & (value >> 24),
            0xff & (value >> 16),
            0xff & (value >> 8),
            0xff & value,
        )

    def readint(self, address):
        result = bytearray(5)
        with self.tmcdev as spi:
            spi.write(bytes([address, 0, 0, 0, 0]))
            spi.write(bytes([address, 0, 0, 0, 0]))
            spi.readinto(result)
        print(result)
        value = 0
        for i in range(4):
            value = (value << 8) | result[i+1]
        return value

    def setGlobalConfig(self, recalibrate=False, fast_stand_still=0, enable_pwm=False,
                        multistep_filter=False, invert=False, diag0_error=True,
                        diag0_over_temp=True, diag0_stall=False, diag1_stall=False,
                        diag1_index=False, diag1_chop=False, diag1_step_skip=False,
                        diag0_push_pull=False, diag1_push_pull=False, small_hysteresis=False,
                        stop_enable=False, direct_mode=False, test_mode=False):
        bits = [test_mode, direct_mode, stop_enable, small_hysteresis,
                diag1_push_pull, diag0_push_pull, diag1_step_skip, diag1_chop,
                diag1_index, diag1_stall, diag0_stall, diag0_over_temp,
                diag0_error, invert, multistep_filter, enable_pwm,
                fast_stand_still, recalibrate]

        self.writeint(GCONF, sum(int(v) << idx for idx, v in enumerate(reversed(bits))))

    def setMode(self, soft_stop=False, stallguard_stop=True, latch_encoder=False,
                latch_r_inactive=False, latch_r_active=False, latch_l_inactive=False,
                latch_l_active=False, swap_lr=False, pol_stop_r=0, pol_stop_l=0,
                stop_r=False, stop_l=False):

        bits = [stop_l, stop_r, pol_stop_l, pol_stop_r, swap_lr, latch_l_active,
                latch_l_inactive, latch_r_active, latch_r_inactive, latch_encoder,
                stallguard_stop, soft_stop]
        self.writeint(SW_MODE, sum(int(v) << idx for idx, v in enumerate(reversed(bits))))

    def setEncoderMode(self, decimal=1, latch_actual=False, clear_counter=False,
                       negative_edge=0, positive_edge=0, clear_once=False,
                       clear_always=False, ignore_ab=False, n_pol=0, b_pol=0, a_pol=0):
        
        bits = [a_pol, b_pol, n_pol, ignore_ab, clear_always, clear_once,
                positive_edge, negative_edge, clear_counter, latch_actual,
                decimal]

        self.writeint(ENCMODE, sum(int(v) << idx for idx, v in enumerate(reversed(bits))))

    def setCurrentScaler(self, scale):
        self.writeint(GLOBAL_SCALER, scale)

    def setDriverCurrent(self, hold, run, hold_delay=6):
        self.write(IHOLD_IRUN, 0, hold_delay, int(run//(self.max_i/32)),
            int(hold//(self.max_i/32)))

    def setPowerDownDelay(self, delay):
        """delay time (s) after stand still of the 
        motor to motor current power down."""
        self.writeint(TPOWERDOWN, delay)

    def setPwmThreshold(self, threshold):
        """upper velocity for StealthChop voltage PWM mode."""
        self.writeint(TPWMTHRS, threshold)

    def setPwmConfig(self, pwm_limit=12, pwm_regulation=4, freewheel=0,
                     pwm_autogradient=True, pwm_autoscale=True, pwm_frequency=0,
                     pwm_gradient=0, pwm_offset=30):
        assert(pwm_limit < 16)
        assert(pwm_regulation < 16)
        assert(freewheel < 4)
        assert(pwm_frequency < 4)
        assert(pwm_gradient < 256)
        assert(pwm_offset < 256)

        bits = [
            pwm_offset,
            pwm_gradient << 8,
            pwm_frequency << 16,
            pwm_autoscale << 18,
            pwm_autogradient << 19,
            freewheel << 20,
            pwm_regulation << 24,
            pwm_limit << 28
        ]

        self.writeint(PWMCONF, sum(bits))

    def setCoolStepThreshold(self, threshold):
        """lower threshold velocity for switching on smart
        energy CoolStep and StallGuard feature."""
        self.writeint(TCOOLTHRS, threshold)

    def setCoolStepConfig(self, sg_filter=False, sg_threshold=0, i_min=0,
                          stepdown_speed=0, se_max=15, stepup_speed=0, se_min=1):
        assert(stepup_speed < 4)
        assert(stepdown_speed < 4)
        assert(se_min < 16)
        assert(se_max < 16)
        assert(sg_threshold < 128)

        bits = [
            se_min,
            stepup_speed << 5,
            se_max << 8,
            stepdown_speed << 13,
            i_min << 15,
            sg_threshold << 16,
            sg_filter << 24
        ]

        self.writeint(COOLCONF, sum(bits))

    def setChopperConfig(self, disable_vs_short=False, disable_gnd_short=False,
                         double_edge_step=False, interpolation=False, microsteps=0,
                         tpfd=0, high_velocity=False, high_velocity_fullstep=False,
                         blank_time=1, chopper_mode=0, fast_decay_mode=0,
                         tfd=0, hysteresis_low=0, hysteresis_start=0, off_time=0):
        assert(off_time < 16)
        assert(hysteresis_start < 8)
        assert(hysteresis_low < 16)
        assert(microsteps < 16)
        assert(tpfd < 16)
        assert(blank_time < 4)

        bits = [
            off_time,
            hysteresis_start << 4,
            hysteresis_low << 7,
            tfd << 11,
            fast_decay_mode << 12,
            chopper_mode << 14,
            blank_time << 15,
            high_velocity_fullstep << 18,
            high_velocity << 19,
            tpfd << 20,
            microsteps << 24,
            interpolation << 28,
            double_edge_step << 29,
            disable_gnd_short << 30,
            disable_vs_short << 31
        ]

        self.writeint(CHOPCONF, sum(bits))

    def setStallMaxThreshold(self, threshold):
        """The stall detection feature becomes switched off for 2-3 
        electrical periods whenever passing THIGH threshold to 
        compensate for the effect of switching modes"""
        self.writeint(THIGH, threshold)

    def setRampMode(self, mode):
        """
        0: Positioning mode (using all A, D and V parameters)
        1: Velocity mode to positive VMAX (using AMAX acceleration)
        2: Velocity mode to negative VMAX (using AMAX acceleration)
        3: Hold mode (velocity remains unchanged, unless stop event occurs)
        """
        self.writeint(RAMPMODE, mode)

    def setActualPosition(self, pos):
        self.writeint(XACTUAL, pos)

    def setStartVelocity(self, v):
        self.writeint(VSTART, v)

    def setStartAcceleration(self, a):
        self.writeint(A1, a)
    
    def setStartThresholdVelocity(self, v):
        self.writeint(V1, v)

    def setMaxAcceleration(self, a):
        self.writeint(AMAX, a)

    def setMaxVelocity(self, v):
        self.writeint(VMAX, v)

    def setStopDeceleration(self, a):
        self.writeint(D1, a)
    
    def setStopVelocity(self, v):
        self.writeint(VSTOP, v)

    def setZeroWait(self, t):
        self.writeint(TZEROWAIT, t)

    def setTargetPosition(self, pos):
        self.writeint(XTARGET, pos)

    def setDcStepMinVelocity(self, v):
        self.writeint(VDCMIN, v)

    def setEncoderConstant(self, const):
        self.writeint(ENC_CONST, const)

    def setEncoderDeviation(self, steps):
        self.writeint(ENC_DEVIATION, steps)

    def enableSPI(self):
        if self.tmc_mode is not None:
            self.tmc_mode.value = 0

    def enableStandalone(self):
        if self.tmc_mode is not None:
            self.tmc_mode.value = 1

    def reset(self):
        self.tmc_en.value = 0
        time.sleep(0.001)
        self.tmc_en.value = 1

    def init(self):
        self.enableSPI()
        self.reset()

        self.setGlobalConfig(enable_pwm=True)
        self.setPwmThreshold(500)
        self.setPwmConfig(pwm_offset=200, pwm_gradient=1, pwm_autoscale=1)
        self.setChopperConfig(off_time=3, hysteresis_start=4, hysteresis_low=1, blank_time=2)

        self.setStartVelocity(1)
        self.setRampMode(MODE_POSITION)
        self.setActualPosition(0)
        self.setTargetPosition(0)

        self.setDriverCurrent(hold=0.2, run=1.8)

        if self.standalone:
            # Re-enable sd_mode standalone
            self.enableStandalone()
