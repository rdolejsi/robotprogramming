from utime import ticks_us, ticks_diff

from light_driver import LightDriver

if __name__ == "__main__":
    __run__ = "__light_test__"

    lights = LightDriver()

    try:
        if __run__ == "__light_test__":
            phase_length = 2000 * 1000
            phase_start = ticks_us()
            phase_report_length = 250 * 1000
            phase_report_start = phase_start
            phase = "init"
            phases = ["init", "beam", "brake", "rev", "rev_off", "brake_off", "beam_off", "stop"]
            while len(phases) > 0:
                phase_diff = ticks_diff(ticks_us(), phase_start)
                if phase_diff >= phase_length:
                    phase_start = ticks_us()
                    phase = phases[0]
                    phases = phases[1:]
                    print("Phase %s, time_diff %d" % (phase, phase_diff))
                    if phase == "init":
                        lights.head_on()
                        lights.back_on()
                    if phase == "beam":
                        lights.beam_on()
                    if phase == "brake":
                        lights.brake_on()
                    if phase == "rev":
                        lights.reverse_on()
                    if phase == "rev_off":
                        lights.reverse_off()
                    if phase == "brake_off":
                        lights.brake_off()
                    if phase == "beam_off":
                        lights.beam_off()
                    if phase == "stop":
                        lights.off()
                lights.update()

    finally:
        lights.off()
        lights.update()
        print("Finished")
