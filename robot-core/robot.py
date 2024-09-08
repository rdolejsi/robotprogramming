from light_driver import LightDriver
from microbit import pin2
from time import ticks_ms, ticks_diff, sleep


class Robot:
    def __init__(self):
        self.light_driver = LightDriver()
        self.supply_voltage_pin = pin2

    def get_supply_voltage(self):
        """Returns the current supply voltage of the robot."""
        adc = self.supply_voltage_pin.read_analog()  # ADC value 0 - 1023
        # Convert ADC value to volts: 3.3 V / 1024 (max. voltage at ADC pin / ADC resolution)
        voltage = 0.00322265625 * adc
        # Multiply measured voltage by voltage divider ratio to calculate actual voltage
        # (10 kOhm + 5,6 kOhm) / 5,6 kOhm [(R1 + R2) / R2, Voltage divider ratio]
        return voltage * 2.7857142

    def update(self):
        """Updates the robot and its subsystems."""
        self.light_driver.update()


if __name__ == "__main__":
    robot = Robot()
    phases = [
        "start",
        "print supply voltage"
        "end"
    ]
    phase_length = 5000
    phase_start = ticks_ms()
    phase = "start"
    while len(phases) > 0:
        if ticks_diff(ticks_ms(), phase_start) > phase_length:
            phase_start = ticks_ms()
            phase = phases[0]
            phases = phases[1:]
            print("Phase %s" % phase)
            if phase == "print supply voltage":
                print("Supply voltage: %.2f V" % robot.get_supply_voltage())
        robot.update()
        sleep(0.01)
    print("Done")
