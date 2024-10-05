from cely_projekt import Robot, Konstanty, Obrazovka

from microbit import button_a, sleep
from math import sin, cos, pi

def lokalizuj(x, y, uhel, prikaz):
    if prikaz == Konstanty.ROVNE:
        x_nove = cos(uhel) * 1 + x  # posunuli jsme se po mřížce přesně o 1
        y_nove = sin(uhel) * 1 + y  # posunuli jsme se po mřížce přesně o 1
    elif prikaz == Konstanty.VZAD:
        x_nove = cos(uhel) * -1 + x
        y_nove = sin(uhel) * -1 + y
    else:
        x_nove = x
        y_nove = y
    return x_nove, y_nove

def lokalizuj_uhel(uhel, prikaz):
    if prikaz == Konstanty.VLEVO:
        return uhel + pi/2
    elif prikaz == Konstanty.VPRAVO:
        return uhel - pi/2
    else:
        return uhel

if __name__ == "__main__":

    prikazy = [Konstanty.ROVNE]

    robot = Robot(0.15, 0.067, prikazy, False)

    st_start = "start"
    st_jed_po_care = "jed_po_care"
    st_krizovatka = "krizovatka"
    st_ztracen = "ztracen"
    st_exit = "exit"

    aktualni_stav = st_start
    Obrazovka.pis(aktualni_stav)

    x = 0
    y = 0
    uhel = 0

    try:
        while not button_a.was_pressed():

            if aktualni_stav == st_start:
                Obrazovka.pis(aktualni_stav)
                if robot.inicializuj():
                    aktualni_stav = st_jed_po_care

            elif aktualni_stav == st_jed_po_care:
                Obrazovka.pis(aktualni_stav)
                robot.jed_po_care(0.1, 0.5)
                situace = robot.vycti_senzory_cary()

                if situace == Konstanty.KRIZOVATKA:
                    aktualni_stav = st_krizovatka
                elif situace == Konstanty.CARA:
                    aktualni_stav = st_jed_po_care
                elif situace == Konstanty.ZTRACEN:
                    Obrazovka.pis(aktualni_stav)
                    robot.jed(0, 0)
                    # aktualni_stav = st_exit
                    aktualni_stav = st_ztracen

            elif aktualni_stav == st_krizovatka:
                Obrazovka.pis(aktualni_stav)
                x, y = lokalizuj(x, y, uhel)
                aktualni_stav = st_exit

            elif aktualni_stav == st_ztracen:
                Obrazovka.pis(aktualni_stav)
                robot.jed(0, 0)
                aktualni_stav = st_jed_po_care

            elif aktualni_stav == st_exit:
                Obrazovka.pis(aktualni_stav)
                robot.jed(0, 0)
                break

            robot.aktualizuj_se()
            sleep(5)

    finally:
        robot.jed(0, 0)
        # Obrazovka.pis("S")
