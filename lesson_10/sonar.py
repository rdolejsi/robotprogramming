from microbit import pin8, pin12, button_a
from machine import time_pulse_us

class Sonar:
    """Handles the ultrasonic sensor HC-SR04 to measure distance in cm.
    Based on https://cdn.sparkfun.com/datasheets/Sensors/Proximity/HCSR04.pdf,
    The sensor operates at freq 40Hz and supports ranges from 2cm to 400cm,
    with 0.3cm resolution and 3mm precision, providing a viewing angle of 15 degrees.
    The sensor uses the speed of sound in the air to calculate the distance.
    Trigger Input Signal 10uS TTL pulse is used to start the ranging,
    and the module will send out an 8 cycle burst of ultrasound at 40 kHz
    and raise its echo. The Echo Output Signal is an input TTL lever signal
    and the range in proportion to the duration of the echo signal."""
    SOUND_SPEED = 343  # m/s

    def __init__(self, trigger_pin=pin12, echo_pin=pin8):
        self.trigger_pin = trigger_pin
        self.trigger_pin.write_digital(0)
        self.echo_pin = echo_pin
        self.echo_pin.read_digital()

    def get_distance_cm(self):
        self.trigger_pin.write_digital(1)
        self.trigger_pin.write_digital(0)

        measured_time_us = time_pulse_us(self.echo_pin, 1)
        if measured_time_us < 0:
            return measured_time_us

        measured_time_sec = measured_time_us / 1000000
        distance_cm = 100 * measured_time_sec * self.SOUND_SPEED / 2
        return distance_cm
