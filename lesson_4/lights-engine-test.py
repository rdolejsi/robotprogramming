from NeoPixel import NeoPixel
from microbit import i2c
from microbit import sleep

i2c_speed = 100 * 1000  # 100kHz
debug_enabled = True

def debug(message):
    """Prints a debug message if debug is enabled."""
    if debug_enabled is True:
        print(message)

def assert_true(test: bool, message: str, **kvargs):
    if not test:
        raise ValueError(message % kvargs)

class Light:
    def __init__(self, lights: NeoPixel, address):
        assert_true(address < 8, "Light address %s out of range 0..7" % address)
        self.lights = lights
        self.address = address
        self.color = (255, 255, 255)
        self.enabled = False
        self.off()

    def on(self):
        """Switches the light on."""
        debug("Switching on light %d w/ color %s" % (self.address, self.color))
        self.lights[self.address] = self.color
        self.lights.write()
        self.enabled = True

    def off(self):
        """Switches the light off."""
        debug("Switching off light %d" % self.address)
        self.lights[self.address] = (0, 0, 0)
        self.lights.write()
        self.enabled = False

    def set_color(self, color):
        """Alters color of the light when enabled. Does not turn the light on."""
        new_state = "on" if self.enabled is True else "off"
        debug("Changing light %d (currently %s) color to %s" % (self.address, new_state, color))
        self.color = color

    def get_color(self):
        """Returns the current color of the light (irrespective if it's enabled or not)."""
        return self.color

class Engine:
    class Direction:
        right_fwd = 3
        right_rwd = 2
        left_rwd = 4
        left_fwd = 5
        all = [right_fwd, right_rwd, left_fwd, left_rwd]

    def __init__(self, address):
        self.address = address
        debug("Initializing engine at %d" % self.address)
        self.handshake_i2c()

    def set_speed(self, direction, speed):
        params = (self.address, direction, speed)
        print('Setting engine at address %d to direction %d, speed %d' % params)
        i2c.write(self.address, bytes([direction, speed]))

    def stop(self, direction, speed):
        params = (self.address, direction, speed)
        print('Setting engine at address %d to direction %d, speed %d' % params)
        i2c.write(self.address, bytes([direction, speed]))

    def handshake_i2c(self):
        i2c.write(self.address, b"\x00\x01")
        i2c.write(self.address, b"\xE8\xAA")


if __name__ == "__main__":
    i2c.init(i2c_speed)
    adresy = i2c.scan()

    print(adresy)
    for adresa in adresy:
        print(hex(adresa))

    engine = Engine(0x70)
    for direction in Engine.Direction.all:
        engine.set_speed(direction, 135)
        sleep(5000)
        engine.set_speed(direction, 0)
