from microbit import i2c, pin2


class System:
    I2C_ADDRESS = 0x70
    I2C_FREQ = 100_000
    I2C_SENSOR_DEVICE = 0x38

    SENSOR_DATA_LINE_LEFT = 0x80
    SENSOR_DATA_LINE_CENTER = 0x40
    SENSOR_DATA_LINE_RIGHT = 0x40
    SENSOR_DATA_IR_LEFT = 0x20
    SENSOR_DATA_IR_RIGHT = 0x10

    def __init__(self, i2c_freq=I2C_FREQ, voltage_pin=pin2):
        self.voltage_pin = voltage_pin
        i2c.init(freq=i2c_freq)

    def i2c_write(self, data):
        i2c.write(self.I2C_ADDRESS, data)

    def get_line_sensors(self):
        """Returns the current state of the line sensors (left, center, right)."""
        data = i2c.read(self.I2C_SENSOR_DEVICE, 1)
        return (
            bool(data[0] & self.SENSOR_DATA_LINE_LEFT),
            bool(data[0] & self.SENSOR_DATA_LINE_CENTER),
            bool(data[0] & self.SENSOR_DATA_LINE_RIGHT)
        )

    def get_ir_sensors(self):
        """Returns the current state of the IR sensors (left, right)."""
        data = i2c.read(self.I2C_SENSOR_DEVICE, 1)
        return (
            bool(data[0] & self.SENSOR_DATA_IR_LEFT),
            bool(data[0] & self.SENSOR_DATA_IR_RIGHT)
        )

    def get_supply_voltage(self):
        """Returns the current supply voltage of the robot."""
        adc = self.voltage_pin.read_analog()  # ADC value 0 - 1023
        # Convert ADC value to volts: 3.3 V / 1024 (max. voltage at ADC pin / ADC resolution)
        voltage = 0.00322265625 * adc
        # Multiply measured voltage by voltage divider ratio to calculate actual voltage
        # (10 kOhm + 5,6 kOhm) / 5,6 kOhm [(R1 + R2) / R2, Voltage divider ratio]
        return voltage * 2.7857142
