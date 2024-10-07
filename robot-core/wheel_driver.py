from microbit import pin14, pin15

from system import System
from wheel import Wheel


class WheelDriver:
    """Handles the movement of the whole robot
        (forward, backward, turning). Activities are either
        indefinite or conditional based on ticks, time
        or real speed measured by the encoder on wheel level."""

    def __init__(self, system: System,
                 left_pwm_min=50, left_pwm_max=255, left_pwm_multiplier=0, left_pwm_shift=0,
                 right_pwm_min=50, right_pwm_max=255, right_pwm_multiplier=0, right_pwm_shift=0):
        """Initializes the wheel driver."""
        self.system = system
        self.system.i2c_write(b"\x00\x01")
        self.system.i2c_write(b"\xE8\xAA")
        self.left = Wheel(system=system, name="left",
                          motor_fwd_cmd=5, motor_rwd_cmd=4, sensor_pin=pin14,
                          pwm_min=left_pwm_min, pwm_max=left_pwm_max,
                          pwm_multiplier=left_pwm_multiplier, pwm_shift=left_pwm_shift)
        self.right = Wheel(system=system, name="right",
                           motor_fwd_cmd=3, motor_rwd_cmd=2, sensor_pin=pin15,
                           pwm_min=right_pwm_min, pwm_max=right_pwm_max,
                           pwm_multiplier=right_pwm_multiplier, pwm_shift=right_pwm_shift)
        self.stop()

    # Please note: normally, we would have aggregate move...() methods here for both wheels, but
    # these got removed in favor of smaller code memory footprint + we control each wheel separately anyway.

    def stop(self):
        """Stops the robot."""
        self.left.stop()
        self.right.stop()

    def update(self):
        """Updates the wheel driver, propagating the changes to the hardware."""
        self.left.update()
        self.right.update()
