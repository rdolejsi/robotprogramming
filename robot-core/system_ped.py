from time import monotonic_ns, sleep

from board import P2
from picoed import i2c, display

from system import System as SystemBase


class System(SystemBase):
    VOLTAGE_PIN = P2

    def __init__(self, i2c_freq=SystemBase.I2C_FREQ):
        super().__init__()
        i2c.init(freq=i2c_freq)

    def get_system_type(self):
        return self.SYS_PICO

    def ticks_us(self):
        return monotonic_ns() // 1000

    def ticks_diff(self, ticks1, ticks2):
        return abs(ticks1 - ticks2)

    def sleep_us(self, us):
        sleep(us / 1_000_000)

    def i2c_scan(self) -> list[int]:
        while not i2c.try_lock():
            pass
        ret = i2c.scan()
        i2c.unlock()
        return ret

    def i2c_read(self, addr: int, n: int) -> bytes:
        while not i2c.try_lock():
            pass
        buffer = bytearray(n)
        i2c.readfrom_into(addr, buffer, start=0, end=n)
        i2c.unlock()
        return buffer

    def i2c_write(self, addr: int, buf: bytes):
        while not i2c.try_lock():
            pass
        i2c.writeto(addr, buf)
        i2c.unlock()

    def pin_read_digital(self, pin):
        # todo: implement this
        pass

    def pin_write_digital(self, pin, value: int):
        # todo: implement this
        pass

    def set_sonar_angle_pwm(self, angle_pwm: int):
        # todo: implement this
        pass

    def trigger_sonar(self, value: int):
        # todo: implement this
        pass

    def get_sonar_echo(self):
        # todo: implement this
        pass

    def measure_sonar_echo_time(self) -> int:
        # todo: implement this
        pass

    def get_encoder_pin_left(self):
        # todo: implement this
        pass

    def get_encoder_pin_right(self):
        # todo: implement this
        pass

    def get_adc_value(self) -> int:
        return P2.read_analog()

    def is_button_a_pressed(self):
        # todo: implement this
        pass

    def is_button_b_pressed(self):
        # todo: implement this
        pass

    def display_text(self, label):
        display.text(label[0,3])
        print("Label: %s" % label)

    def display_sensors(self, ll, lc, lr, il, ir, y=4, lb=9, ib=5):
        # todo: implement this
        pass

    def display_drive_mode(self, mode):
        # todo: implement this
        pass

    def get_drive_mode_symbol_keys(self):
        # todo: implement this
        pass

    def display_speed(self, speed_now, speed_max):
        # todo: implement this
        pass

    def display_bitmap(self, x_pos: int, y_pos: int, width: int, lines: list[int]):
        # todo: implement this
        pass

    def display_clear(self):
        # todo: implement this
        pass

    def display_on(self):
        # todo: implement this
        pass

    def display_off(self):
        # todo: implement this
        pass
