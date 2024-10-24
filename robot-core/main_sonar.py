from sonar import Sonar
from system import System

if __name__ == "__main__":
    # __run__ = "__sonar_angles__"
    # __run__ = "__sonar_distance__"
    __run__ = "__sonar_scanner__"

    system = System()
    sonar = Sonar(system=system, scan_range_max=0.5, scan_interval=250_000)

    try:
        if __run__ == "__sonar_angles__":
            for angle in range(-90, 90):
                sonar.set_angle(angle)
                system.sleep_us(250_000)

        elif __run__ == "__sonar_distance__":
            while not system.is_button_a_pressed():
                distance = sonar.get_distance()
                if distance < 0:
                    print("Error %f while getting distance value" % distance)
                else:
                    print("Distance %fm" % sonar.get_distance())
                system.sleep_us(250_000)

        elif __run__ == "__sonar_scanner__":
            sonar.start_scan()
            while not system.is_button_a_pressed():
                sonar.update()

    finally:
        sonar.stop_scan()
        sonar.set_angle(0)
        print("Finished")
