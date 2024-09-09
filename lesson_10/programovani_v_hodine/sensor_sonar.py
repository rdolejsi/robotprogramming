from microbit import pin8, pin12, button_a
from machine import time_pulse_us

from time import sleep

class UltrasoundSensor:
    SOUND_SPEED = 343  # m/s

    def __init__(self):
        self.trigger_pin = pin12
        self.trigger_pin.write_digital(0)
        self.echo_pin = pin8
        self.echo_pin.read_digital()

    # def measure_distance1(self):
    #     self.trigger_pin.write_digital(1)
    #     sleep(10)
    #     self.trigger_pin.write_digital(0)
    #     while self.echo_pin.read_digital() == 0:
    #         pass
    #     start_time = ticks_us()
    #     while self.echo_pin.read_digital() == 1:
    #         pass
    #     end_time = ticks_us()
    #     return (end_time - start_time) / 58

    def measure_distance_cm(self):
        self.trigger_pin.write_digital(1)
        self.trigger_pin.write_digital(0)

        measured_time_us = time_pulse_us(self.echo_pin, 1)
        if measured_time_us < 0:
            return measured_time_us

        measured_time_sec = measured_time_us / 1000000
        distance_cm = 100 * measured_time_sec * self.SOUND_SPEED / 2
        return distance_cm

if __name__ == "__main__":
    sensor = UltrasoundSensor()
    while not button_a.is_pressed():
        print(sensor.measure_distance_cm())
        sleep(1000)
