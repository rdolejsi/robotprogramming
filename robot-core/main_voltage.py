from system import System

if __name__ == "__main__":
    __run__ = "__print_voltage__"

    system = System()

    try:
        if __run__ == "__print_voltage__":
            while not system.is_button_a_pressed():
                voltage = system.get_supply_voltage()
                system.display_text("%fV supply voltage" % voltage)
                system.sleep_us(500_000)

    finally:
        print("Finished")
