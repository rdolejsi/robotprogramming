from microbit import pin14, pin15, i2c

from wheel import Wheel


class WheelDriver:
    """Handles the movement of the whole robot
        (forward, backward, turning). Activities are either
        indefinite or conditional based on ticks, time
        or real speed measured by the speedometer on wheel level."""
    I2C_ADDRESS = 0x70

    def __init__(self):
        """Initializes the wheel driver."""
        i2c.init(freq=100000)
        i2c.write(self.I2C_ADDRESS, b"\x00\x01")
        i2c.write(self.I2C_ADDRESS, b"\xE8\xAA")
        self.wheel_left = Wheel(i2c_address=self.I2C_ADDRESS,
                                motor_fwd_cmd=5, motor_rwd_cmd=4, sensor_pin=pin14)
        self.wheel_right = Wheel(i2c_address=self.I2C_ADDRESS,
                                 motor_fwd_cmd=3, motor_rwd_cmd=2, sensor_pin=pin15)

    def move(self, speed_left, speed_right):
        """Moves the robot with the given speed for each wheel."""
        self.wheel_left.move(speed_left)
        self.wheel_right.move(speed_right)

    def move_by_ticks(self, speed_left, speed_right, distance_ticks_left, distance_ticks_right):
        """Moves the robot with the given speed for each wheel for given distance."""
        self.wheel_left.move_by_ticks(speed_left, distance_ticks_left)
        self.wheel_right.move_by_ticks(speed_right, distance_ticks_right)

    def move_by_time(self, speed_left, speed_right, distance_time_ms):
        """Moves the robot with the given speed for each wheel for the given time."""
        self.wheel_left.move_by_time(speed_left, distance_time_ms)
        self.wheel_right.move_by_time(speed_right, distance_time_ms)

    def stop(self):
        """Stops the robot."""
        self.wheel_left.stop()
        self.wheel_right.stop()

    def update(self):
        """Updates the wheel driver, propagating the changes to the hardware."""
        self.wheel_left.update()
        self.wheel_right.update()

    def get_speed_cm_per_sec(self):
        """Returns the current speed of the robot."""
        return self.wheel_left.speed, self.wheel_right.speed

    def get_speedometer(self):
        """Returns the left and right speedometer of the robot's wheels."""
        return self.wheel_left.speedometer, self.wheel_right.speedometer
