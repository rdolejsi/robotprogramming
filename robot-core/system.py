from microbit import pin2


class System:
    @staticmethod
    def get_supply_voltage():
        """Returns the current supply voltage of the robot."""
        adc = pin2.read_analog()  # ADC value 0 - 1023
        # Convert ADC value to volts: 3.3 V / 1024 (max. voltage at ADC pin / ADC resolution)
        voltage = 0.00322265625 * adc
        # Multiply measured voltage by voltage divider ratio to calculate actual voltage
        # (10 kOhm + 5,6 kOhm) / 5,6 kOhm [(R1 + R2) / R2, Voltage divider ratio]
        return voltage * 2.7857142
