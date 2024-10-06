from microbit import sleep, button_a

from sonar import Sonar

if __name__ == "__main__":
    # __run__ = "__sonar_angles__"
    # __run__ = "__sonar_distance__"
    __run__ = "__sonar_scanner__"

    sonar = Sonar(scan_range_max=0.5, scan_interval=250_000)

    try:
        if __run__ == "__sonar_angles__":
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

        elif __run__ == "__sonar_scanner__":
            sonar.start_scan()
            while not button_a.is_pressed():
                sonar.update()

    finally:
        sonar.stop_scan()
        sonar.set_angle(0)
        print("Finished")
