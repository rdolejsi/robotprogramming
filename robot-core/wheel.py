from time import ticks_ms, ticks_diff

from microbit import i2c

from wheel_speedometer import WheelSpeedometer


class Wheel:
    """Handles single wheel capable of moving forward or backward
    with given (variable) speed and stop immediately or conditionally
    based on distance and time."""

    def __init__(self, i2c_address, motor_fwd_cmd, motor_rwd_cmd, sensor_pin):
        """Initializes the wheel."""
        self.i2c_address = i2c_address
        self.motor_fwd_cmd = motor_fwd_cmd
        self.motor_rwd_cmd = motor_rwd_cmd
        self.sensor_pin = sensor_pin
        self.sensor_value = 0
        self.distance_remain_ticks = 0
        self.distance_req_time_ms = 0
        self.distance_start_time_ms = 0
        self.speed = 0
        self.speedometer = WheelSpeedometer()

    def move(self, speed):
        """Moves the wheel with the given speed (indefinite ticks, time).
        The wheel will continue to move until stop() is called.
        The speed is a value between -100 and 100, where 0 means stop."""
        self.set_speed(speed)
        self.distance_remain_ticks = -1
        self.distance_req_time_ms = -1

    def move_by_ticks(self, speed, distance_ticks):
        """Moves the wheel forward with the given speed for the given distance
        in sensor ticks. If the motor is already moving, the asked distance is added
        to the remaining distance and the motor continues until no distance remains."""
        self.set_speed(speed)
        self.distance_remain_ticks += distance_ticks

    def move_by_time(self, speed, distance_time_ms):
        """Moves the wheel forward with the given speed for the given time.
        If the motor is already moving, the distance in time is added to the current
        distance and the motor continues to move until the total time is reached."""
        self.set_speed(speed)
        self.distance_req_time_ms += distance_time_ms
        if self.distance_start_time_ms == 0:
            self.distance_start_time_ms = ticks_ms()

    def set_speed(self, speed):
        """Sets the wheel speed (and direction). Does not affect the remaining
        distance or time previously set to perform. If the wheel was going
        in the other direction, resets the H-bridge other direction first."""
        if speed == 0:
            print("Stopping the wheel")
            i2c.write(self.i2c_address, bytes([self.motor_fwd_cmd, 0]))
            i2c.write(self.i2c_address, bytes([self.motor_rwd_cmd, 0]))
            return
        speed = max(-255, min(255, speed))
        if (self.speed < 0 < speed) or (self.speed > 0 > speed):
            # if we are changing the direction, we need to reset the motor first
            motor_reset_cmd = self.motor_rwd_cmd if speed >= 0 else self.motor_fwd_cmd
            print("Changing wheel direction, resetting cmd %d speed %d" % (motor_reset_cmd, 0))
            i2c.write(self.i2c_address, bytes([motor_reset_cmd, 0]))
        motor_set_cmd = self.motor_fwd_cmd if speed > 0 else self.motor_rwd_cmd
        print("Setting wheel cmd %d speed %d" % (motor_set_cmd, abs(speed)))
        i2c.write(self.i2c_address, bytes([motor_set_cmd, abs(speed)]))
        self.speed = speed

    def stop(self):
        """Stops the wheel immediately."""
        self.set_speed(0)
        self.distance_remain_ticks = -1
        self.distance_req_time_ms = -1

    def stop_on_no_work(self):
        """Stops the wheel if the remaining distance in ticks or time is reached."""
        stop_due_to_ticks = False
        if self.distance_remain_ticks == 0:
            stop_due_to_ticks = True
        stop_due_to_time = False
        if self.distance_req_time_ms > 0:
            time_delta = ticks_diff(ticks_ms(), self.distance_start_time_ms)
            if time_delta >= self.distance_req_time_ms:
                stop_due_to_time = True
        # we stop only if both conditions are met
        # otherwise we keep the other condition finish as well
        if stop_due_to_ticks and stop_due_to_time:
            self.stop()

    def on_tick(self):
        """Updates the wheel state based on a new tick,
        checks the remaining distance in ticks."""
        self.speedometer.on_tick()
        if self.distance_remain_ticks > 0:
            self.distance_remain_ticks -= 1
            if self.distance_remain_ticks == 0:
                self.stop_on_no_work()

    def get_sensor_value(self):
        """Returns the current sensor value."""
        return self.sensor_pin.read_digital()

    def update(self):
        """Retrieves the sensor value, checks for change and updates the wheel state
        based on the ongoing command."""
        sensor_value_now = self.get_sensor_value()
        if sensor_value_now != self.sensor_value:
            self.sensor_value = sensor_value_now
            self.on_tick()
        self.stop_on_no_work()
