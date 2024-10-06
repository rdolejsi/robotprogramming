from wheel_driver import WheelDriver
from wheel_calibrator import WheelCalibrator

if __name__ == "__main__":
    __run__ = "__calibration_approx__"
    # __run__ = "__calibration_full__"

    wheels = WheelDriver()

    try:
        if __run__ == "__calibration_approx__":
            for wheel in [wheels.left, wheels.right]:
                c = WheelCalibrator(wheel=wheel)
                c.gather_pwm_to_real_speed_table_approx()
                c.calibration_table_to_csv()

        if __run__ == "__calibration_full__":
            for wheel in [wheels.left, wheels.right]:
                c = WheelCalibrator(wheel=wheel)
                c.gather_pwm_to_real_speed_table_full()
                c.calibration_table_to_csv()

    finally:
        wheels.stop()
        print("Finished")
