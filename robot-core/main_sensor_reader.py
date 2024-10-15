from microbit import button_a, i2c
from utime import ticks_us, ticks_diff

from system import System

if __name__ == "__main__":
    # Tries to track a line, stop at first indecision (no line for 3 secs, intersection).
    SPEED = 0.20

    system = System()
    system.display_on()
    try:
        info_cycle_length = 1_000_000
        info_cycle_start = ticks_us()

        while not button_a.is_pressed():
            time_now = ticks_us()
            if ticks_diff(time_now, info_cycle_start) > info_cycle_length:
                info_cycle_start = time_now
                l, c, r, li, ri = system.get_sensors()
                raw = system.i2c_read_sensors()
                print("Line(left=%s, center=%s, right=%s), Obstacle(left=%s, right=%s), raw data=%x (%s)" %
                      (l, c, r, li, ri, raw, bin(raw)))
    finally:
        system.display_off()
        print("Finished")
