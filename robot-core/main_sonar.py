from microbit import sleep, button_a

from sonar import Sonar

if __name__ == "__main__":
    __run__ = "__sonar_angles__"

    sonar = Sonar()

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

    finally:
        sonar.set_angle(0)
        print("Finished")
