from microbit import i2c, sleep
from microbit import pin2, pin14, pin15, pin0
from microbit import display

from utime import ticks_us, ticks_diff

class K:
    NEDEFINOVANO = "nedefinovano"

    LEVY = "levy"
    PRAVY = "pravy"

    DOPREDU = "dopredu"
    DOZADU = "dozadu"

    ENKODER = "enkoder"
    PR_ENKODER = PRAVY + "_" + ENKODER
    LV_ENKODER = LEVY + "_" + ENKODER

    IR = "IR"
    PR_IR = PRAVY + "_" + IR
    LV_IR = LEVY + "_" + IR

    SENZOR_CARY = "senzor_cary"
    PR_S_CARY = PRAVY + "_" + SENZOR_CARY
    LV_S_CARY = LEVY + "_" + SENZOR_CARY
    PROS_S_CARY = "prostredni_" + SENZOR_CARY

    PI = 3.14159265359

    CARA = "cara"
    KRIZOVATKA = "krizovatka"
    ZTRACEN = "ztracen"
    ZATOC = "zatoc"

    ROVNE = "rovne"
    VPRAVO = "vpravo"
    VLEVO = "vlevo"
    VZAD = "vzad"

    VSE = "vse"


class Senzory:

    def __init__(self, nova_verze=True, debug=False):
        self.nova_verze = nova_verze
        self.DEBUG = debug
        i2c.init(400000)

    def precti_senzory(self):
        surova_data_byte = i2c.read(0x38, 1)
        if self.DEBUG:
            print("surova data", surova_data_byte)
        bitove_pole = self.__byte_na_bity(surova_data_byte)

        senzoricka_data = {}

        if not self.nova_verze:
            senzoricka_data[K.LV_ENKODER] = bitove_pole[9]
            senzoricka_data[K.PR_ENKODER] = bitove_pole[8] #TODO pretipuj taky, ale otestuj!

        senzoricka_data[K.LV_S_CARY] = bool(int(bitove_pole[7]))
        senzoricka_data[K.PROS_S_CARY] = bool(int(bitove_pole[6]))
        senzoricka_data[K.PR_S_CARY] = bool(int(bitove_pole[5]))
        senzoricka_data[K.LV_IR] = bool(int(bitove_pole[4]))
        senzoricka_data[K.PR_IR] = bool(int(bitove_pole[3]))

        return senzoricka_data

    def __byte_na_bity(self, data_bytes):

        data_int = int.from_bytes(data_bytes, "big")
        bit_pole_string = bin(data_int)

        if self.DEBUG:
            print("data_int", data_int)
            print("bit pole", bit_pole_string)

        return bit_pole_string

class Enkoder:

    def __init__(self, jmeno, perioda_rychlosti=1, nova_verze=True, debug=False):
        self.jmeno = jmeno
        self.perioda_rychlosti = perioda_rychlosti*1000000  # na us

        self.nova_verze = nova_verze
        self.tiky = 0
        self.posledni_hodnota = -1
        self.tiky_na_otocku = 40
        self.nova_verze = nova_verze
        self.DEBUG = debug
        self.inicializovano = False
        self.cas_posledni_rychlosti = ticks_us()
        self.radiany_za_sekundu = 0

        if not self.nova_verze:
            self.senzory = Senzory(False, debug)

    def inicializuj(self):
        self.posledni_hodnota = self.aktualni_hodnota()
        self.inicializovano = True

    def aktualni_hodnota(self):
        if self.nova_verze:
            if self.jmeno == K.PR_ENKODER:
                return pin15.read_digital()
            elif self.jmeno == K.LV_ENKODER:
                return pin14.read_digital()
            else:
                return -2
        else:
            senzoricka_data = self.senzory.precti_senzory()

            if self.jmeno == K.LV_ENKODER or self.jmeno == K.PR_ENKODER:
                return int(senzoricka_data[self.jmeno])
            else:
                return -2

    def aktualizuj_se(self):
        if self.DEBUG:
            print("v aktualizuj", self.tiky)
        if self.posledni_hodnota == -1:
            if self.DEBUG:
                print("posledni_hodnota neni nastavena", self.posledni_hodnota)
            return -1

        aktualni_enkoder = self.aktualni_hodnota()
        if self.DEBUG:
            print("aktualni enkoder", aktualni_enkoder)

        if aktualni_enkoder >= 0:  # nenastaly zadne chyby
            if self.posledni_hodnota != aktualni_enkoder:
                self.posledni_hodnota = aktualni_enkoder
                self.tiky += 1
        else:
            return aktualni_enkoder

        return 0

    def us_na_s(self, cas):
        return cas/1000000

    def vypocti_rychlost(self):
        cas_ted = ticks_us()
        interval_us = ticks_diff(cas_ted, self.cas_posledni_rychlosti)
        if interval_us >= self.perioda_rychlosti:
            interval_s = self.us_na_s(interval_us)
            otacky = self.tiky/self.tiky_na_otocku
            radiany = otacky * 2 * K.PI
            self.radiany_za_sekundu = radiany / interval_s
            self.tiky = 0
            self.cas_posledni_rychlosti = cas_ted

        return self.radiany_za_sekundu

class Motor:
    def __init__(self, jmeno, prumer_kola, kalibrace, nova_verze=True, debug=False):
        if jmeno == K.LEVY:
            self.__kanal_dopredu = b"\x05"
            self.__kanal_dozadu = b"\x04"
        elif jmeno == K.PRAVY:
            self.__kanal_dopredu = b"\x03"
            self.__kanal_dozadu = b"\x02"
        else:
            raise AttributeError("spatne jmeno motoru, musi byt \"levy\" a nebo \"pravy\", zadane jmeno je" + str(jmeno))

        self.__kalibrace = kalibrace

        self.__DEBUG = debug
        self.__jmeno = jmeno
        self.__prumer_kola = prumer_kola
        self.__enkoder = Enkoder(jmeno + "_enkoder", 1, nova_verze, debug)
        self.__smer = K.NEDEFINOVANO
        self.__inicializovano = False
        self.__rychlost_byla_zadana = False
        self.__min_pwm = 0
        self.__perioda_regulace = 1000000 #v microsekundach
        self.__cas_posledni_regulace = 0
        self.aktualni_rychlost = 0

    def inicializuj(self):
        i2c.write(0x70, b"\x00\x01")
        i2c.write(0x70, b"\xE8\xAA")

        self.__enkoder.inicializuj()
        self.__inicializovano = True
        self.__cas_posledni_regulace = ticks_us()

    def jed_doprednou_rychlosti(self, v: float):
        if not self.__inicializovano:
            return -1

        self.__pozadovana_uhlova_r_kola = self.__dopredna_na_uhlovou(v)
        if self.__DEBUG:
            print("pozadovana uhlova", self.__pozadovana_uhlova_r_kola)

        self.__rychlost_byla_zadana = True

        prvni_PWM = self.__uhlova_na_PWM(abs(self.__pozadovana_uhlova_r_kola))
        if self.__DEBUG:
            print("prvni_PWM", prvni_PWM)

        if self.__pozadovana_uhlova_r_kola > 0:
            self.__smer = K.DOPREDU
        elif self.__pozadovana_uhlova_r_kola < 0:
            self.__smer = K.DOZADU
        else: # = 0
            self.__smer == K.NEDEFINOVANO

        return self.__jed_PWM(prvni_PWM)


    def __dopredna_na_uhlovou(self, v: float):
        return v/(self.__prumer_kola/2)

    def __uhlova_na_PWM(self, uhlova):

        if uhlova == 0: #TODO uvazuj, zda tohle by nemelo byt pod min rozjezd rychlost
            return 0
        else:
            return int(self.__kalibrace.a*uhlova + self.__kalibrace.b)

    def __jed_PWM(self, PWM):
        je_vse_ok = -2
        omezeni = False

        if PWM > 255:
            PWM = 255
            omezeni = True

        if PWM < 0:
            PWM = 0
            omezeni = True

        if self.__smer == K.DOPREDU:
            je_vse_ok  = self.__nastav_PWM_kanaly(self.__kanal_dopredu, self.__kanal_dozadu, PWM)
        elif self.__smer == K.DOZADU:
            je_vse_ok  = self.__nastav_PWM_kanaly(self.__kanal_dozadu, self.__kanal_dopredu, PWM)
        elif self.__smer == K.NEDEFINOVANO:
            if PWM == 0:
                je_vse_ok = self.__nastav_PWM_kanaly(self.__kanal_dozadu, self.__kanal_dopredu, PWM)
            else:
                je_vse_ok = -1
        else:
            je_vse_ok = -3

        if je_vse_ok == 0 and omezeni:
            return -4
        else:
            return je_vse_ok

    def __nastav_PWM_kanaly(self, kanal_on, kanal_off, PWM):
        # TODO zkontroluj, ze motor byl inicializovan
        i2c.write(0x70, kanal_off + bytes([0]))
        i2c.write(0x70, kanal_on + bytes([PWM]))
        self.__PWM = PWM
        return 0

    def aktualizuj_se(self):
        self.__enkoder.aktualizuj_se()
        cas_ted = ticks_us()
        cas_rozdil = ticks_diff(cas_ted, self.__cas_posledni_regulace)
        navratova_hodnota = 0
        if cas_rozdil > self.__perioda_regulace:
            navratova_hodnota = self.__reguluj_otacky()
            self.__cas_posledni_regulace = cas_ted

        return navratova_hodnota

    def __reguluj_otacky(self):

        if not self.__inicializovano:
            return -1

        if not self.__rychlost_byla_zadana:
            return -2

        P = 6

        self.aktualni_rychlost = self.__enkoder.vypocti_rychlost()

        if self.__pozadovana_uhlova_r_kola < 0:
            self.aktualni_rychlost *= -1

        error = self.__pozadovana_uhlova_r_kola - self.aktualni_rychlost
        akcni_zasah = P*error
        return self.__zmen_PWM_o(akcni_zasah)

    def __zmen_PWM_o(self, akcni_zasah):

        akcni_zasah = int(akcni_zasah)

        if self.__smer == K.DOZADU:
            akcni_zasah *= -1

        nove_PWM = self.__PWM + akcni_zasah

        return self.__jed_PWM(nove_PWM)

class Robot:

    def __init__(self, rozchod_kol: float, prumer_kola: float, kalibrace_levy, kalibrace_pravy, nova_verze=True):
        """
        Konstruktor tridy
        """
        self.__d = rozchod_kol/2
        self.__prumer_kola = prumer_kola

        self.__levy_motor = Motor(K.LEVY, self.__prumer_kola, kalibrace_levy, nova_verze)
        self.__pravy_motor = Motor(K.PRAVY, self.__prumer_kola, kalibrace_pravy, nova_verze)
        self.__inicializovano = False
        self.__cas_minule_reg = ticks_us()
        self.__perioda_regulace = 1000000
        self.__senzory = Senzory(nova_verze)

        self.__perioda_cary_us = 75000

        self.__posledni_cas_popojeti = 0

    def inicializuj(self):
        i2c.init(400000)
        self.__levy_motor.inicializuj()
        self.__pravy_motor.inicializuj()
        self.__inicializovano = True

        self.__posledni_cas_reg_cary_us = ticks_us()

        self.jed(0,0)
        return True

    # pokrocily ukol 7
    def jed(self, dopredna_rychlost: float, uhlova_rychlost: float):
        """Pohybuj se zadanym  pohybem slozenym z dopredne rychlosti v a uhlove rychlosti"""

        if not self.__inicializovano:
            return -1

        self.__dopredna_rychlost = dopredna_rychlost
        self.__uhlova_rychlost = uhlova_rychlost
        # kinematika diferencionalniho podvozku - lekce 7
        dopr_rychlost_leve = dopredna_rychlost - self.__d * uhlova_rychlost
        dopr_rychlost_prave = dopredna_rychlost + self.__d * uhlova_rychlost

        # nevolam povely i2c rovnou - to bych rozbijela zapouzdreni trid
        # vyuziji funkce tridy motor
        self.__levy_motor.jed_doprednou_rychlosti(dopr_rychlost_leve)
        self.__pravy_motor.jed_doprednou_rychlosti(dopr_rychlost_prave)

        return 0


    # zmer napajeci napeti robota
    def zmer_a_vrat_napajeci_napeti(self):
        return 0.00898 * pin2.read_analog()

    def __aktualni_rychlost(self):
        levy_r = self.__levy_motor.aktualni_rychlost * self.__prumer_kola/2
        pravy_r = self.__pravy_motor.aktualni_rychlost * self.__prumer_kola/2


        omega = (pravy_r - levy_r)/ (2 * self.__d)
        v = levy_r + self.__d * omega
        print("aktualizuju", levy_r, pravy_r, v, omega)
        return v, omega

    def aktualizuj_se(self):
        self.__levy_motor.aktualizuj_se()
        self.__pravy_motor.aktualizuj_se()

        if ticks_diff(ticks_us(), self.__cas_minule_reg) > self.__perioda_regulace:
            self.__cas_minule_reg = ticks_us()

    def vycti_senzory_cary(self):

        senzoricka_data = self.__senzory.precti_senzory()

        if senzoricka_data[K.LV_S_CARY] and senzoricka_data[K.PR_S_CARY]:
            return K.KRIZOVATKA
        if senzoricka_data[K.LV_S_CARY] and senzoricka_data[K.PROS_S_CARY]:
            return K.KRIZOVATKA
        if senzoricka_data[K.PROS_S_CARY] and senzoricka_data[K.PR_S_CARY]:
            return K.KRIZOVATKA

        elif not senzoricka_data[K.LV_S_CARY] and not senzoricka_data[K.PR_S_CARY] and not senzoricka_data[K.PROS_S_CARY]:
            return K.ZTRACEN
        else:
            return K.CARA

    def jed_po_care(self, dopredna, uhlova):
        cas_ted = ticks_us()

        if ticks_diff(cas_ted, self.__posledni_cas_reg_cary_us) > self.__perioda_cary_us:
            self.__posledni_cas_reg_cary_us = cas_ted
            data = self.__senzory.precti_senzory()

            if data[K.LV_S_CARY]:
                self.jed(dopredna, uhlova)

            if data[K.PR_S_CARY]:
                self.jed(dopredna, -uhlova)

            if not data[K.LV_S_CARY] and not data[K.PR_S_CARY]:
                self.jed(dopredna, 0)

    def popojed(self, dopredna, perioda_us):

        if self.__posledni_cas_popojeti == 0:
            self.__posledni_cas_popojeti = ticks_us()

        cas_ted = ticks_us()
        if ticks_diff(cas_ted, self.__posledni_cas_popojeti) > perioda_us:
            self.__posledni_cas_popojeti = 0
            self.jed(0,0)
            return True
        else:
            self.jed(dopredna, 0)
            return False

class Obrazovka:
    def pis(text):
        display.show(text[0])
        print(text)

class KalibracniFaktory:

    def __init__(self, min_rychlost, min_pwm_rozjezd, min_pwm_dojezd, a, b):
        self.min_rychlost = min_rychlost
        self.min_pwm_rozjezd = min_pwm_rozjezd
        self.min_pwm_dojezd = min_pwm_dojezd
        self.a = a
        self.b = b
