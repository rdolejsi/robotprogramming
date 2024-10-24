from system import System
from wheel_calibrator import WheelCalibrator
from wheel_driver import WheelDriver

if __name__ == "__main__":
    __run__ = "__calibration_approx__"
    # __run__ = "__calibration_full__"

    system = System()
    wheels = WheelDriver(system=system)

    try:
        if __run__ == "__calibration_approx__":
            print("Approximate calibration running..")
            for wheel in [wheels.left, wheels.right]:
                c = WheelCalibrator(system=system, wheel=wheel)
                c.gather_pwm_to_real_speed_table_approx()
                c.calibration_table_to_csv()

        if __run__ == "__calibration_full__":
            print("Full calibration running..")
            for wheel in [wheels.left, wheels.right]:
                c = WheelCalibrator(system=system, wheel=wheel)
                c.gather_pwm_to_real_speed_table_full()
                c.calibration_table_to_csv()

    finally:
        wheels.stop()
        print("Finished")
