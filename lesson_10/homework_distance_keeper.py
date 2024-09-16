from time import ticks_ms, ticks_diff, sleep

from microbit import button_a, button_b

from wheel_driver import WheelDriver
from sonar import Sonar

#  Naimplementujte adaptivní tempomat s využitím třídy Robot
#  a dalších vzorových kódů. Využijte zpětné vazby a regulátoru P.
#
# Robot by měl
# - Udržovat minimální vzdálenost 0.2m před překážkou
# - Zastavit se a případně rozjet vzad, pokud je překážka moc blízko
# - Omezit maximální rychlost na 0.3 m/s
if __name__ == "__main__":
    wheel_driver = WheelDriver()
    sonar = Sonar()
    try:
        info_cycle_length = 1000
        info_cycle_start = ticks_ms()
        backoff_speed_pwm = -90
        forward_speed_pwm_initial = 70
        forward_speed_pwm_multiplier = 0.1
        while not button_a.is_pressed():
            # Tries to maintain the robot around 20 cm in front of an obstacle.
            # We use Sonar to measure distance to the obstacle and gradually increase
            # Speed of the robot to 30 cm/s. We also support backing off when too close.
            # We allow for +/- 2 cm around the target distance to avoid oscillation.
            # Please note: issuance of stop on direction reversal is a Wheel feature,
            # we don't need to concern ourselves with it.
            distance_cm = sonar.get_distance_cm()
            if distance_cm > 21:
                # When moving forward, we increase the PWM speed gradually using
                # distance error correction and a predefined speed increase multiplier.
                # The speed is limited to 30 cm/s.
                speed_cm_left, speed_cm_right = wheel_driver.get_speed_cm_per_sec()
                speed_pwm_left, speed_pwm_right = wheel_driver.get_speed_pwm()
                if speed_cm_left < 30:
                    delta_left = forward_speed_pwm_multiplier * (30 - speed_cm_left)
                    new_speed_pwm_left = speed_pwm_left + delta_left
                    delta_right = forward_speed_pwm_multiplier * (30 - speed_cm_right)
                    new_speed_pwm_right = speed_pwm_right + delta_right
                    wheel_driver.move_pwm(new_speed_pwm_left, new_speed_pwm_right)
                else:
                    wheel_driver.move_pwm(30, 30)
            elif distance_cm < 18:
                # If the distance is less than 15 cm, the robot stops and moves
                # backwards until the distance is greater than 20 cm.
                # The reverse direction is constant for now.
                wheel_driver.move_pwm_for_distance(backoff_speed_pwm,
                                                   backoff_speed_pwm, 20 - distance_cm)

            wheel_driver.update()
            sleep(0.01)
            if ticks_diff(ticks_ms(), info_cycle_start) > info_cycle_length:
                info_cycle_start = ticks_ms()
                speed_cm_left, speed_cm_right = wheel_driver.get_speed_cm_per_sec()
                print_params = (distance_cm, speed_cm_left, speed_cm_right)
                print("Distance: %f cm, speed: L=%.2f cm/s, R=%.2f cm/s" % print_params)
        print("Done")
    finally:
        wheel_driver.stop()
