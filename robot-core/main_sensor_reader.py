from system import System

if __name__ == "__main__":
    # Tries to track a line, stop at first indecision (no line for 3 secs, intersection).
    SPEED = 0.20

    system = System()
    system.display_on()
    try:
        info_cycle_length = 1_000_000
        info_cycle_start = system.ticks_us()
        drive_mode_symbol_keys = list(system.get_drive_mode_symbol_keys())
        drive_mode_symbol_keys_index = 0
        drive_mode_symbol_keys_redraw_countdown = 1

        while not system.is_button_a_pressed():
            time_now = system.ticks_us()
            if system.ticks_diff(time_now, info_cycle_start) > info_cycle_length:
                info_cycle_start = time_now
                l, c, r, li, ri = system.get_sensors()
                system.display_sensors(l, c, r, li, ri)
                raw = system.i2c_read_sensors()
                print("Line(left=%s, center=%s, right=%s), Obstacle(left=%s, right=%s), raw data=%x (%s)" %
                      (l, c, r, li, ri, raw, bin(raw)))
                if drive_mode_symbol_keys_redraw_countdown > 0:
                    drive_mode_symbol_keys_redraw_countdown -= 1
                else:
                    system.display_drive_mode(drive_mode_symbol_keys[drive_mode_symbol_keys_index])
                    drive_mode_symbol_keys_index = (drive_mode_symbol_keys_index + 1) % len(drive_mode_symbol_keys)
                    drive_mode_symbol_keys_redraw_countdown = 1
    finally:
        system.display_off()
        print("Finished")