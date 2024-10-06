from microbit import sleep, button_a
from utime import ticks_us, ticks_diff

from light_driver import LightDriver
from wheel_driver import WheelDriver
from sonar import Sonar
from wheel_calibrator import WheelCalibrator

if __name__ == "__main__":
    # __run__ = "__basic_motor__"
    __run__ = "__calibration_approx__"

    light_driver = LightDriver()
    wheel_driver = WheelDriver()
    sonar = Sonar()

    try:
        if __run__ == "__basic_motor__":
            phase_length = 2000 * 1000
            phase_start = ticks_us()
            phase = "init"
            phases = ["start", "forward", "backward", "stop"]
            while len(phases) > 0:
                if ticks_diff(ticks_us(), phase_start) > phase_length:
                    phase_diff = ticks_diff(ticks_us(), phase_start)
                    phase_start = ticks_us()
                    phase = phases[0]
                    phases = phases[1:]
                    print("Phase %s, time_diff %d" % (phase, phase_diff))
                    if phase == "start":
                        wheel_driver.stop()
                        light_driver.head_on()
                        light_driver.back_on()
                    if phase == "forward":
                        wheel_driver.wheel_left.move_pwm(100)
                        wheel_driver.wheel_right.move_pwm(100)
                    if phase == "backward":
                        wheel_driver.wheel_left.move_pwm(-100)
                        wheel_driver.wheel_right.move_pwm(-100)
                    if phase == "stop":
                        wheel_driver.stop()
                wheel_driver.update()
                light_driver.update()

        elif __run__ == "__calibration_approx__":
            for wheel in [wheel_driver.wheel_left, wheel_driver.wheel_right]:
                wheel_calibrator = WheelCalibrator(wheel=wheel)
                wheel_calibrator.gather_pwm_to_real_speed_table_approx()
                wheel_calibrator.calibration_table_to_csv()

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
        wheel_driver.stop()
        light_driver.off()
        sonar.set_angle(0)
        print("Finished")
