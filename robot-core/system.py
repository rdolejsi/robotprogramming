from microbit import i2c, pin2

class System:
    I2C_ADDRESS = 0x70
    I2C_FREQ = 100_000
    I2C_SENSOR_DEVICE = 0x38

    MASK_LINE_LEFT = 0x04
    MASK_LINE_CENTER = 0x08
    MASK_LINE_RIGHT = 0x10
    MASK_IR_LEFT = 0x20
    MASK_IR_RIGHT = 0x40

    def __init__(self, i2c_freq=I2C_FREQ, voltage_pin=pin2):
        self.voltage_pin = voltage_pin
        i2c.init(freq=i2c_freq)

    def bit_not(self, n, numbits=8):
        return (1 << numbits) - 1 - n

    def i2c_write(self, data):
        i2c.write(self.I2C_ADDRESS, data)

    def i2c_read_sensors(self):
        """Returns the current sensor data byte."""
        return i2c.read(self.I2C_SENSOR_DEVICE, 1)[0]

    def get_line_sensors(self):
        """Checks if line sensors (left, center, right) detected a line (true if line present)."""
        data = self.i2c_read_sensors()
        l = bool(data & self.MASK_LINE_LEFT)
        c = bool(data & self.MASK_LINE_CENTER)
        r = bool(data & self.MASK_LINE_RIGHT)
        return l, c, r

    def get_ir_sensors(self):
        """Checks if IR sensors (left, right) detected an obstacle (true if obstacle present)."""
        data = self.i2c_read_sensors()
        l = bool(data & self.MASK_IR_LEFT)
        r = bool(data & self.MASK_IR_RIGHT)
        return not l, not r

    def get_supply_voltage(self):
        """Returns the current supply voltage of the robot."""
        adc = self.voltage_pin.read_analog()  # ADC value 0 - 1023
        # Convert ADC value to volts: 3.3 V / 1024 (max. voltage at ADC pin / ADC resolution)
        voltage = 0.00322265625 * adc
        # Multiply measured voltage by voltage divider ratio to calculate actual voltage
        # (10 kOhm + 5,6 kOhm) / 5,6 kOhm [(R1 + R2) / R2, Voltage divider ratio]
        return voltage * 2.7857142
