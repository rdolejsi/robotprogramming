from cely_projekt import Robot, Konstanty, Obrazovka

from microbit import button_a, sleep

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
                robot.jed(0, 0)
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
