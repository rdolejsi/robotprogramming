from time import ticks_ms, ticks_diff
from neopixel import NeoPixel
from microbit import pin0, sleep

class LightMode:
    """Enumeration of light modes supported by the Light class."""
    PLAIN = 0
    BLINK = 1


class Light:
    """Handles a single RGB light capable of holding its state and performing either
    instant operations or operations spread over time (blinking, ...).

    The class is designed to be used in a cooperative multitasking environment,
    where the caller is expected to call update() in a timely manner. The implementation
    maintains its state and indicates when a state should be propagated externally
    (on a change), but does NOT update any external hardware.

    It is expected the caller will use the state to update the hardware when needed.
    This is needed to allow multiple lights to be updated using a single call
    to the hardware, as designed by NeoPixel stripe handler."""

    def __init__(self, position, on_color):
        """Initializes light with the operational color, as turned off."""
        self.position = position
        self.on_color = on_color
        self.state = (0, 0, 0)
        self.changed = True
        self.mode = LightMode.PLAIN
        self.blink_frequency_ms = 0
        self.blink_start_time = 0

    def set_color(self, color):
        """Sets the light color, reflects immediately if the light is turned on."""
        self.on_color = color
        if self.state != (0, 0, 0):
            if self.state != color:
                self.changed = True
                self.state = color

    def on(self):
        """Turns the light on using the current on_color."""
        self.mode = LightMode.PLAIN
        if self.state != self.on_color:
            self.state = self.on_color
            self.changed = True

    def off(self):
        """Turns the light off."""
        self.mode = LightMode.PLAIN
        if self.state != (0, 0, 0):
            self.state = (0, 0, 0)
            self.changed = True

    def blink(self, blink_frequency_ms):
        """Blinks the light between black and on_color with the given frequency."""
        self.mode = LightMode.BLINK
        self.blink_frequency_ms = blink_frequency_ms
        self.blink_start_time = ticks_ms()

    def is_blinking(self, direction):
        """Checks if the light is blinking."""
        return self.mode == LightMode.BLINK

    def update(self):
        """Updates the light state based on the current mode and time."""
        if self.mode == LightMode.BLINK:
            time_delta = ticks_diff(ticks_ms(), self.blink_start_time)
            if time_delta >= self.blink_frequency_ms:
                self.blink_start_time = ticks_ms()
                if self.state == (0, 0, 0):
                    self.state = self.on_color
                else:
                    self.state = (0, 0, 0)
                self.changed = True
        if self.changed is True:
            self.changed = False
            return self.state
        else:
            return None


class LightPlacement:
    """Defines the color scheme and placement used in the Joy-Car Robot."""
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

    WHITE_BRIGHT = (255, 255, 255)
    WHITE_MID = (128, 128, 128)
    WHITE_MILD = (60, 60, 60)
    ORANGE = (100, 35, 0)
    RED_BRIGHT = (255, 0, 0)
    RED_MILD = (60, 0, 0)

    initial_color_for_position = [
        WHITE_MILD, ORANGE, ORANGE, WHITE_MILD,
        ORANGE, RED_MILD, RED_MILD, ORANGE
    ]


class LightDriver:
    """Handles the light subsystem of Joy-Car Robot, utilizing NeoPixel light strip.
    Each light is represented by a Light object, which is capable of maintaining
    its state and providing it when an update is needed on the hardware side."""

    def __init__(self):
        """Initializes the light driver with all lights initially switched off."""
        self.lights = [
            Light(idx, on_color=LightPlacement.initial_color_for_position[idx])
            for idx in range(8)
        ]
        self.neopixel = NeoPixel(pin0, 8)
        # controls the shared lights for headlight and beam headlight indication
        # with the following priority: reverse (left only, see placement) > brake > back
        self.head_enabled = False  # keeps headlight on after beam lights go off
        self.beam_enabled = False  # keeps headlight on after beam lights go off
        # controls the shared lights for back, brake and reverse indication
        # with the following priority: reverse (left only, see placement) > brake > back
        self.back_enabled = False
        self.brake_enabled = False
        self.reverse_enabled = False
        self.update()

    def update(self):
        """Updates the light driver, propagating the changes to the hardware.
        Each light provides its state only if a state propagation is needed,
        otherwise it is skipped. If all lights are up-to-date, no-op is performed."""
        write_required = False
        for light in self.lights:
            light_state = light.update()
            if light_state is not None:
                self.neopixel[light.position] = light_state
                write_required = True
        if write_required:
            self.neopixel.write()

    def head_on(self):
        """Turns the headlights on. If beam headlights are on, lights are unaffected."""
        self.head_enabled = True
        if not self.beam_enabled:
            for light_pos in LightPlacement.headlights:
                self.lights[light_pos].set_color(LightPlacement.WHITE_MILD)
                self.lights[light_pos].on()

    def head_off(self):
        """Turns the headlights off."""
        self.head_enabled = False
        if not self.beam_enabled:
            for light_pos in LightPlacement.headlights:
                self.lights[light_pos].off()

    def beam_on(self):
        """Turns the beam headlights on."""
        self.beam_enabled = True
        for light_pos in LightPlacement.headlights:
            self.lights[light_pos].set_color(LightPlacement.WHITE_BRIGHT)
            self.lights[light_pos].on()

    def beam_off(self):
        """Turns the beam headlights off. If standard headlights are on,
        the shared lights are switched to them."""
        self.beam_enabled = False
        for light_pos in LightPlacement.headlights:
            if self.head_enabled is True:
                self.head_on()
            else:
                self.lights[light_pos].off()

    def blink(self, direction, blink_frequency_ms):
        """Blinks the light(s) indicating the given direction."""
        for position in LightPlacement.blinkers[direction]:
            self.lights[position].blink(blink_frequency_ms)

    def blink_emergency(self, blink_frequency_ms):
        """Blinks all turn-indicating light(s) to signal an emergency."""
        self.blink(LightPlacement.LEFT_DIRECTION, blink_frequency_ms)
        self.blink(LightPlacement.RIGHT_DIRECTION, blink_frequency_ms)

    def blink_off(self):
        """Stops blinking on all blinker lights."""
        for position in LightPlacement.blinkers[LightPlacement.LEFT_DIRECTION]:
            self.lights[position].off()
        for position in LightPlacement.blinkers[LightPlacement.RIGHT_DIRECTION]:
            self.lights[position].off()

    def is_blinking(self, direction):
        """Checks if the light(s) indicating the given direction are blinking."""
        position_first = LightPlacement.blinkers[direction][0]
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
        for light_pos in LightPlacement.backlights:
            light_is_reverse = light_pos in LightPlacement.reverse_lights
            if self.reverse_enabled is True and light_is_reverse:
                self.lights[light_pos].set_color(LightPlacement.WHITE_MID)
                self.lights[light_pos].on()
            elif self.brake_enabled is True:
                self.lights[light_pos].set_color(LightPlacement.RED_BRIGHT)
                self.lights[light_pos].on()
            elif self.back_enabled is True:
                self.lights[light_pos].set_color(LightPlacement.RED_MILD)
                self.lights[light_pos].on()
            else:
                self.lights[light_pos].off()

lights = LightDriver()

def lightsON():
    lights.head_on()
    lights.back_on()
    lights.update()

def lightsOFF():
    lights.head_off()
    lights.back_off()
    lights.update()

def lightsBreakON():
    lights.brake_on()
    lights.update()

def lightsBreakOFF():
    lights.brake_off()
    lights.update()

def lightsBackON():
    lights.reverse_on()
    lights.update()

def lightsBackOFF():
    lights.reverse_off()
    lights.update()

def lightsIndicatorON(direction):
    lights.blink(direction, 400)
    lights.update()

def lightsIndicatorOFF(direction):
    lights.blink_off()
    lights.update()

if __name__ == "__main__":
    # Application example
    print("lightsON")
    lightsON()       # Light on
    sleep(5000)
    print("lightsBreakON")
    lightsBreakON()  # Brake light on
    sleep(5000)
    print("lightsBreakOFF")
    lightsBreakOFF()  # Brake light off
    sleep(5000)
    print("lightsBackON")
    lightsBackON()  # Reversing lights on
    sleep(5000)
    print("lightsBackOFF")
    lightsBackOFF()  # Reversing lights off
    sleep(5000)
    start_time = ticks_ms()
    print("lightIndicatorON")
    lightsIndicatorON(LightPlacement.LEFT_DIRECTION)  # Left indicator on
    while ticks_diff(ticks_ms(), start_time) < 5000:
        lights.update()
        sleep(0.01)
    print("lightIndicatorOFF")
    lightsIndicatorOFF(LightPlacement.LEFT_DIRECTION)  # Left indicator off
    sleep(5000)
    start_time = ticks_ms()
    print("lightEmergencyON")
    lights.blink_emergency(200)  # Emergency indicator, super fast
    while ticks_diff(ticks_ms(), start_time) < 5000:
        lights.update()
        sleep(0.01)
    print("lightBlinkOFF")
    lights.blink_off()
    sleep(5000)
    lightsIndicatorOFF(LightPlacement.LEFT_DIRECTION)  # Left indicator off
    print("lightsOFF")
    lightsOFF()  # Light off
