from time import ticks_ms, ticks_diff, sleep

from microbit import button_a, button_b

from wheel_driver import WheelDriver
from wheel_calibrator import WheelCalibrator

from sonar import Sonar

#  Naimplementujte adaptivní tempomat s využitím třídy Robot
#  a dalších vzorových kódů. Využijte zpětné vazby a regulátoru P.
#
# Robot by měl
# - Udržovat minimální vzdálenost 0.2m před překážkou
# - Zastavit se a případně rozjet vzad, pokud je překážka moc blízko
# - Omezit maximální rychlost na 0.3 m/s
if __name__ == "__main__":
    wheel_driver = WheelDriver(left_pwm_min=60, left_pwm_multiplier=0.1809153, left_pwm_shift=-5.509312,
                               right_pwm_min=60, right_pwm_multiplier=0.1628194, right_pwm_shift=-5.216122)
    sonar = Sonar()
    try:
        regulation_cycle_length = 1000
        regulation_cycle_start = ticks_ms()
        speed_pwm_min = 70
        speed_cm_max = 30
        distance_cm_desired = 20
        distance_cm_tolerance = 2

        speed_target = 130
        speed_actual = 120
        speed_change_angle = 2

        while not button_a.is_pressed() and speed_actual <= speed_target:
            wheel_driver.update()

            if ticks_diff(ticks_ms(), regulation_cycle_start) > regulation_cycle_length:
                regulation_cycle_start = ticks_ms()
                speed_error = speed_target - speed_actual
                speed_alter = speed_change_angle * speed_error
                print("Speed error: %d, speed alter: %d" % (speed_error, speed_alter))
                speed_actual += 2

        print("Done")
    finally:
        wheel_driver.stop()
