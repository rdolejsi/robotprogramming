from light import Light
from system import System


class LightDriver:
    """Handles the light subsystem of Joy-Car Robot, utilizing NeoPixel light strip.
    Each light is represented by a Light object, which is capable of maintaining
    its state and providing it when an update is needed on the hardware side."""
    LEFT_DIRECTION = 0
    RIGHT_DIRECTION = 1

    blinkers = {
        LEFT_DIRECTION: [1, 4],
        RIGHT_DIRECTION: [2, 7]
    }
    headlights = [0, 3]
    backlights = [5, 6]
    # Only one light is used for reverse, other stays as back or brake light
    reverse_lights = [5]

    WHITE_BRIGHT = (180, 180, 180)
    WHITE_MID = (90, 90, 90)
    WHITE_MILD = (30, 30, 30)
    ORANGE = (100, 35, 0)
    RED_BRIGHT = (255, 0, 0)
    RED_MILD = (30, 0, 0)

    initial_color_for_position = [
        WHITE_MILD, ORANGE, ORANGE, WHITE_MILD,
        ORANGE, RED_MILD, RED_MILD, ORANGE
    ]

    def __init__(self, system: System):
        """Initializes the light driver with all lights initially switched off."""
        self.system = system
        self.neopixel = None  # we will be initializing lights on demand to spare memory
        self.lights = [
            Light(system, idx, on_color=self.initial_color_for_position[idx])
            for idx in range(8)
        ]
        # controls the shared lights for headlight and beam headlight indication
        # with the following priority: reverse (left only, see placement) > brake > back
        self.head_enabled = False  # keeps headlight on after beam lights go off
        self.beam_enabled = False  # keeps headlight on after beam lights go off
        # controls the shared lights for back, brake and reverse indication
        # with the following priority: reverse (left only, see placement) > brake > back
        self.back_enabled = False
        self.brake_enabled = False
        self.reverse_enabled = False
        self.off()
        self.update()

    def update(self):
        """Updates the light driver, propagating the changes to the hardware.
        Each light provides its state only if a state propagation is needed,
        otherwise it is skipped. If all lights are up-to-date, no-op is performed."""
        write_required = False
        for light in self.lights:
            light_state = light.update()
            if light_state is not None:
                self.set_light(light.position, light_state)
                write_required = True
        if write_required:
            self.update_lights()

    def head_on(self):
        """Turns the headlights on. If beam headlights are on, lights are unaffected."""
        self.head_enabled = True
        if not self.beam_enabled:
            for light_pos in self.headlights:
                self.lights[light_pos].set_color(self.WHITE_MILD)
                self.lights[light_pos].on()

    def head_off(self):
        """Turns the headlights off."""
        self.head_enabled = False
        if not self.beam_enabled:
            for light_pos in self.headlights:
                self.lights[light_pos].off()

    def beam_on(self):
        """Turns the beam headlights on."""
        self.beam_enabled = True
        for light_pos in self.headlights:
            self.lights[light_pos].set_color(self.WHITE_BRIGHT)
            self.lights[light_pos].on()

    def beam_off(self):
        """Turns the beam headlights off. If standard headlights are on,
        the shared lights are switched to them."""
        self.beam_enabled = False
        for light_pos in self.headlights:
            if self.head_enabled is True:
                self.head_on()
            else:
                self.lights[light_pos].off()

    def blink(self, direction, blink_frequency_us):
        """Blinks the light(s) indicating the given direction."""
        for position in self.blinkers[direction]:
            self.lights[position].blink(blink_frequency_us)

    def blink_emergency(self, blink_frequency_us):
        """Blinks all turn-indicating light(s) to signal an emergency."""
        self.blink(self.LEFT_DIRECTION, blink_frequency_us)
        self.blink(self.RIGHT_DIRECTION, blink_frequency_us)

    def blink_off(self):
        """Stops blinking on all blinker lights."""
        for position in self.blinkers[self.LEFT_DIRECTION]:
            self.lights[position].off()
        for position in self.blinkers[self.RIGHT_DIRECTION]:
            self.lights[position].off()

    def is_blinking(self, direction):
        """Checks if the light(s) indicating the given direction are blinking."""
        position_first = self.blinkers[direction][0]
        return self.lights[position_first].is_blinking()

    def off(self):
        """Turns all the lights off."""
        for light in self.lights:
            light.off()

    def back_on(self):
        """Turns the backlights on. If brake lights are on, shared lights
        are unaffected. Enabled reverse lights is also unaffected."""
        self.back_enabled = True
        self.update_back()

    def back_off(self):
        """Turns the backlights off."""
        self.back_enabled = False
        self.update_back()

    def brake_on(self):
        """Turns the brake lights on."""
        self.brake_enabled = True
        self.update_back()

    def brake_off(self):
        """Turns the brake lights off. If backlights are on,
        the shared lights are switched to them, kept on."""
        self.brake_enabled = False
        self.update_back()

    def reverse_on(self):
        """Turns the reverse light on."""
        self.reverse_enabled = True
        self.update_back()

    def reverse_off(self):
        """Turns the reverse light off."""
        self.reverse_enabled = False
        self.update_back()

    def update_back(self):
        """Updates the backlights based on the current state of shared back,
        brake and reverse lights. The priority is reverse > brake > back.
        If reverse is on, only the reverse light is on."""
        for light_pos in self.backlights:
            light_is_reverse = light_pos in self.reverse_lights
            if self.reverse_enabled is True and light_is_reverse:
                self.lights[light_pos].set_color(self.WHITE_MID)
                self.lights[light_pos].on()
            elif self.brake_enabled is True:
                self.lights[light_pos].set_color(self.RED_BRIGHT)
                self.lights[light_pos].on()
            elif self.back_enabled is True:
                self.lights[light_pos].set_color(self.RED_MILD)
                self.lights[light_pos].on()
            else:
                self.lights[light_pos].off()

    # The following methods are hardware-specific and should be in system-specific classes.
    # However, due to Micro:Bit memory constrains, we touch lights only if needed to fit in its memory.
    # Hence, the work with Neopixel is excluded from the main system implementation and even happens in runtime only.

    def init_lights_if_needed(self):
        """Initializes the lights if they are not initialized yet."""
        if self.system.get_system_type() == System.SYS_MBIT:
            if self.neopixel is None:
                from neopixel import NeoPixel
                from microbit import pin0
                self.neopixel = NeoPixel(pin0, 8)
        elif self.system.get_system_type() == System.SYS_PICO:
            pass
        pass

    def set_light(self, light: int, state: int):
        """Sets the state of a light."""
        if self.system.get_system_type() == System.SYS_MBIT:
            self.init_lights_if_needed()
            self.neopixel[light] = state
        elif self.system.get_system_type() == System.SYS_PICO:
            # Implementation for CircuitPython is pending
            pass
        pass

    def update_lights(self):
        """Updates the state of all lights."""
        if self.system.get_system_type() == System.SYS_MBIT:
            self.init_lights_if_needed()
            self.neopixel.write()
        elif self.system.get_system_type() == System.SYS_PICO:
            # Implementation for CircuitPython is pending
            pass
        pass
