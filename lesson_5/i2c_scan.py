from microbit import i2c
from microbit import sleep

i2c_speed = 100000

class Direction:
    right_fwd = 3
    right_rwd = 2
    left_rwd = 4
    left_fwd = 5
    all = [right_fwd, right_rwd, left_fwd, left_rwd]

class Engine:
    def __init__(self, address):
        self.address = address
        print('Initializing engine at %d' % self.address)
        i2c.write(self.address, b"\x00\x01")
        i2c.write(self.address, b"\xE8\xAA")
        pass

    def set_speed(self, direction, speed):
        params = (self.address, direction, speed)
        print('Setting engine at address %d to direction %d, speed %d' % params)
        i2c.write(self.address, bytes([direction, speed]))


if __name__ == "__main__":
    i2c.init(i2c_speed)
    adresy = i2c.scan()

    print(adresy)
    for adresa in adresy:
        print(hex(adresa))

    engine = Engine(0x70)
    for direction in Direction.all:
        engine.set_speed(direction, 135)
        sleep(5000)
        engine.set_speed(direction, 0)
