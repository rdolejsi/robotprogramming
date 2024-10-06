from microbit import sleep, button_a
from utime import ticks_us, ticks_diff

from light_driver import LightDriver
from wheel_driver import WheelDriver
from sonar import Sonar
from wheel_calibrator import WheelCalibrator

if __name__ == "__main__":
    __run__ = "__basic_motor__"
    # __run__ = "__calibration_approx__"

    lights = LightDriver()
    wheels = WheelDriver()
    sonar = Sonar()

    try:
        if __run__ == "__basic_motor__":
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
                    if phase == "start":
                        wheels.stop()
                        lights.head_on()
                        lights.back_on()
                    if phase == "forward":
                        wheels.left.move_pwm(255)
                        wheels.right.move_pwm(255)
                    if phase == "backward":
                        wheels.left.move_pwm(-200)
                        wheels.right.move_pwm(-200)
                    if phase == "stop":
                        wheels.stop()
                wheels.update()
                lights.update()

        elif __run__ == "__calibration_approx__":
            for wheel in [wheels.left, wheels.right]:
                c = WheelCalibrator(wheel=wheel)
                c.gather_pwm_to_real_speed_table_approx()
                c.calibration_table_to_csv()

        elif __run__ == "__sonar_angles__":
            for angle in range(-90, 90):
                sonar.set_angle(angle)
                sleep(250)

        elif __run__ == "__sonar_distance__":
            while not button_a.is_pressed():
                distance = sonar.get_distance()
                if distance < 0:
                    print("Error %f while getting distance value" % distance)
                else:
                    print("Distance %fm" % sonar.get_distance())
                sleep(250)

    finally:
        wheels.stop()
        lights.off()
        lights.update()
        sonar.set_angle(0)
        print("Finished")
