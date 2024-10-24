from sonar import Sonar
from system import System
from wheel_driver import WheelDriver

if __name__ == "__main__":
    system = System()
    wheels = WheelDriver(
        system=system,
        left_pwm_min=60, left_pwm_multiplier=0.08752789, left_pwm_shift=-2.150176,
        right_pwm_min=60, right_pwm_multiplier=0.08356924, right_pwm_shift=-2.03894
    )
    sonar = Sonar(system=system)
    try:
        # Tries to maintain the robot around 20 cm in front of an obstacle.
        # We use Sonar to measure distance to the obstacle and gradually increase
        # Speed of the robot to 30 cm/s. We also support backing off when too close.
        # We allow for +/- 2 cm around the target distance to avoid oscillation.

        # The wheels are controlled individually and we are trying to keep the robot
        # going straight, so we are aiming at keeping speed in radians constant for
        # both wheels.
        distance_m_desired = 0.2
        distance_m_tolerance = 0.02
        distance_m_max = 0.5
        # with 30 cm/s the robot was a bit sluggish and was not able to respond well
        speed_m_max = 0.3
        speed_m_min = 0.2
        # any wheel can provide below conversion
        speed_rad_max = wheels.left.enc.m2rad(speed_m_max)
        speed_rad_min = wheels.left.enc.m2rad(speed_m_min)
        speed_change_slope = 2

        # Calculate the constants for radsec speed dependency on the distance to ensure
        # the robot won't go fast when the distance is small.
        # When the distance is 50 cm, the speed should be 0.4 m/s.
        # When the distance is 20 cm, the speed should be 0.2 m/s.
        distance_m_to_speed_radsec = (speed_rad_max - speed_rad_min) / (distance_m_max - distance_m_desired)

        info_cycle_length = 1_000_000
        info_cycle_start = system.ticks_us()
        regulation_cycle_length = 200_000
        regulation_cycle_start = system.ticks_us()

        distance = None
        while not system.is_button_a_pressed():
            wheels.update()

            time_now = system.ticks_us()
            if system.ticks_diff(time_now, regulation_cycle_start) > regulation_cycle_length:
                regulation_cycle_start = time_now
                distance = sonar.get_distance()
                if distance > distance_m_max:
                    wheels.stop()
                else:
                    # the back-off distance is very small, we would normally probably use minimal speed,
                    # but it might not work due to the wheel calibration, so we still try to use the same error
                    # correction as for the forward movement. We can use the same mechanism and just indicate
                    # negative pwm speed to move backwards (thanks to our Wheel implementation).
                    if (distance > distance_m_desired + distance_m_tolerance) or \
                            (distance < distance_m_desired - distance_m_tolerance):
                        distance_error = distance - distance_m_desired
                        desired_speed_radsec = abs(distance_error) * distance_m_to_speed_radsec + speed_rad_min

                        current_speed_radsec_left = wheels.left.enc.speed_radsec_avg
                        speed_error_radsec_left = desired_speed_radsec - current_speed_radsec_left
                        speed_change_radsec_left = speed_change_slope * speed_error_radsec_left
                        # print("Current speed %f, Desired speed %f, Speed change left %f" % (current_speed_radsec_left, desired_speed_radsec, speed_change_radsec_left))
                        new_speed_radsec_left = min(current_speed_radsec_left + speed_change_radsec_left, speed_rad_max)
                        new_speed_pwm_left = wheels.left.radsec2pwm(new_speed_radsec_left)

                        current_speed_radsec_right = wheels.right.enc.speed_radsec_avg
                        speed_error_radsec_right = desired_speed_radsec - current_speed_radsec_right
                        speed_change_radsec_right = speed_change_slope * speed_error_radsec_right
                        new_speed_radsec_right = min(
                            current_speed_radsec_right + speed_change_radsec_right,
                            speed_rad_max
                        )
                        # print("Current speed %f, Desired speed %f, Speed change right %f" % (current_speed_radsec_right, desired_speed_radsec, speed_change_radsec_right))
                        new_speed_pwm_right = wheels.right.radsec2pwm(new_speed_radsec_right)

                        if distance_error > 0:
                            wheels.left.move_pwm_for_distance(new_speed_pwm_left, distance_error)
                            wheels.right.move_pwm_for_distance(new_speed_pwm_right, distance_error)
                        else:
                            wheels.left.move_pwm_for_distance(-new_speed_pwm_left, abs(distance_error))
                            wheels.right.move_pwm_for_distance(-new_speed_pwm_right, abs(distance_error))
                    else:
                        wheels.stop()

            if system.ticks_diff(time_now, info_cycle_start) > info_cycle_length:
                info_cycle_start = time_now
                speed_msec_left = wheels.left.enc.speed_msec()
                speed_msec_right = wheels.right.enc.speed_msec()
                print("Distance: %.04fm, speed: L=%.04fm/s, R=%.04fm/s" % (distance, speed_msec_left, speed_msec_right))
    finally:
        wheels.stop()
        print("Finished")
