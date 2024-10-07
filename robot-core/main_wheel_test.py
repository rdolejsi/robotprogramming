from utime import ticks_us, ticks_diff

from system import System
from wheel_driver import WheelDriver

if __name__ == "__main__":
    __run__ = "__wheel_test__"

    wheels = WheelDriver(system=System())

    try:
        if __run__ == "__wheel_test__":
            phase_length = 5000 * 1000
            phase_start = ticks_us()
            phase_report_length = 250 * 1000
            phase_report_start = phase_start
            phase = "init"
            phases = ["forward", "backward", "stop"]
            while len(phases) > 0:
                phase_diff = ticks_diff(ticks_us(), phase_report_start)
                if phase_diff >= phase_report_length:
                    phase_report_start = ticks_us()
                    l_enc = wheels.left.enc
                    lv = l_enc.calc_value
                    lu = l_enc.calc_update_count
                    l_radsec = l_enc.speed_radsec
                    l_radsec_a = l_enc.speed_radsec_avg
                    l_msec = l_enc.speed_msec()
                    r_enc = wheels.right.enc
                    rv = r_enc.calc_value
                    ru = r_enc.calc_update_count
                    r_radsec = r_enc.speed_radsec
                    r_radsec_a = r_enc.speed_radsec_avg
                    r_msec = r_enc.speed_msec()
                    print(
                        "Wheel left %s<-%su: %.06f radsec, %.06f radsec_avg, %.06f msec, Wheel right %s<-%su: %.06f radsec, %.06f radsec_avg, %.06f msec" %
                        (lv, lu, l_radsec, l_radsec_a, l_msec, rv, ru, r_radsec, r_radsec_a, r_msec))
                phase_diff = ticks_diff(ticks_us(), phase_start)
                if phase_diff >= phase_length:
                    phase_start = ticks_us()
                    phase = phases[0]
                    phases = phases[1:]
                    print("Phase %s, time_diff %d" % (phase, phase_diff))
                    if phase == "forward":
                        wheels.left.move_pwm(255)
                        wheels.right.move_pwm(255)
                    if phase == "backward":
                        wheels.left.move_pwm(-200)
                        wheels.right.move_pwm(-200)
                    if phase == "stop":
                        wheels.stop()
                wheels.update()

    finally:
        wheels.stop()
        print("Finished")
