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
        self.system.i2c_init_motor()
        self.left = Wheel(system=system, name="left",
                          motor_fwd_cmd=5, motor_rwd_cmd=4, sensor_pin=system.get_encoder_pin_left(),
                          pwm_min=left_pwm_min, pwm_max=left_pwm_max,
                          pwm_multiplier=left_pwm_multiplier, pwm_shift=left_pwm_shift)
        self.right = Wheel(system=system, name="right",
                           motor_fwd_cmd=3, motor_rwd_cmd=2, sensor_pin=system.get_encoder_pin_right(),
                           pwm_min=right_pwm_min, pwm_max=right_pwm_max,
                           pwm_multiplier=right_pwm_multiplier, pwm_shift=right_pwm_shift)
        self.speed_rad = -99
        self.rotation_rad = -99
        self.stop()

    # Please note: normally, we would have aggregate move...() methods here for both wheels, but
    # these got removed in favor of smaller code memory footprint + we control each wheel separately anyway.

    def move(self, speed_rad, rotation_rad):
        """Moves the robot with specific PWM on each wheel while applying rotational speed in radians.
        Positive rotation is clockwise, negative rotation is counterclockwise.
        We first need to calculate the speed of each wheel based on the desired speed and rotation."""
        if speed_rad == 0 and rotation_rad == 0:
            self.stop()
            return
        reverse = speed_rad < 0
        if reverse:
            rotation_rad = -rotation_rad
        speed_rad = abs(speed_rad)
        left_speed = speed_rad - self.left.enc.WHEEL_CIRCUMFERENCE_M * rotation_rad
        right_speed = speed_rad + self.right.enc.WHEEL_CIRCUMFERENCE_M * rotation_rad
        if reverse:
            left_speed = -left_speed
            right_speed = -right_speed
        # print("Moving with speed %d pwm, rotation %f rad/s, left_pwm %s, right_pwm %s" % (speed_pwm, rotation_rad, left_speed, right_speed))
        self.left.move_rad(left_speed)
        self.right.move_rad(right_speed)
        self.speed_rad = speed_rad
        self.rotation_rad = rotation_rad

    def turn(self, speed_rad):
        """Turns the robot on the spot with specific pwm speed.
        todo: use rotation speed in rad/s and rotation in radians."""
        # if speed_pwm == 0:
        #     self.stop()
        #     return
        # left_speed = -speed_pwm
        # right_speed = speed_pwm
        # print("Turning with speed %d pwm, left_pwm %s, right_pwm %s" % (speed_pwm, left_speed, right_speed))
        # self.left.move_pwm(speed_pwm=left_speed)
        # self.right.move_pwm(speed_pwm=right_speed)
        # self.speed_pwm = speed_pwm
        # self.rotation_rad = -1
        angle = 90 if speed_rad > 0 else -90
        angle_in_rad = angle * 3.141592653589793 / 180
        rad_to_travel = self.left.enc.WHEEL_CENTER_DISTANCE * angle_in_rad
        if angle > 0:
            self.left.move_radsec_for_distance(speed_rad, rad_to_travel)
            self.right.move_radsec_for_distance(-speed_rad, rad_to_travel)
        elif angle < 0:
            self.left.move_radsec_for_distance(-speed_rad, abs(rad_to_travel))
            self.right.move_radsec_for_distance(speed_rad, abs(rad_to_travel))

    def stop(self):
        """Stops the robot."""
        if self.speed_rad == 0 and self.rotation_rad == 0:
            return
        self.left.stop()
        self.right.stop()
        self.speed_rad = 0
        self.rotation_rad = 0

    def update(self):
        """Updates the wheel driver, propagating the changes to the hardware."""
        self.left.update()
        self.right.update()
