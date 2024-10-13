from microbit import button_a
from utime import ticks_us, ticks_diff

from system import System
from wheel_driver import WheelDriver

if __name__ == "__main__":
    # Tries to track a line, stop at first indecision (no line for 3 secs, intersection).
    SPEED = 0.20

    system = System()
    wheels = WheelDriver(
        system=system,
        left_pwm_min=60, left_pwm_multiplier=0.08944848, left_pwm_shift=-2.722451,
        right_pwm_min=60, right_pwm_multiplier=0.08349663, right_pwm_shift=-2.0864
    )
    try:
        info_cycle_length = 1_000_000
        info_cycle_start = ticks_us()
        regulation_cycle_length = 50_000
        regulation_cycle_start = ticks_us()

        while not button_a.is_pressed():
            wheels.update()

            time_now = ticks_us()
            if ticks_diff(time_now, regulation_cycle_start) > regulation_cycle_length:
                regulation_cycle_start = time_now
                # todo: implement the line logic

            if ticks_diff(time_now, info_cycle_start) > info_cycle_length:
                info_cycle_start = time_now
                l, c, r = system.get_line_sensors()

                speed_msec_left = wheels.left.enc.speed_msec()
                speed_msec_right = wheels.right.enc.speed_msec()
                print("Speed: L=%.04fm/s, R=%.04fm/s, l=%s, c=%s, r=%s" % (speed_msec_left, speed_msec_right, l, c, r))
    finally:
        wheels.stop()
        print("Finished")
