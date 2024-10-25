from system import System
from wheel_driver import WheelDriver


class Action:
    def __init__(self, name, symbol, while_sensor, until_sensor):
        self.name = name
        self.symbol = symbol
        self.while_sensor = while_sensor
        self.until_sensor = until_sensor

    def __str__(self):
        return self.name


class SensorMatcher:
    def __init__(self, sensor, min_count, max_count=None):
        self.sensor = sensor
        self.min_count = min_count
        self.max_count = max_count

    def matches(self, sensor, count):
        if sensor != self.sensor:
            return False
        if self.max_count is not None:
            return self.min_count <= count <= self.max_count
        return count >= self.min_count

    # let's print binary representation of the sensor and how many times it needs to match
    def __str__(self):
        return f"{self.sensor:0{5}b} ({self.min_count}x)"


class StateMatcher:
    def __init__(self, steps: list[SensorMatcher]):
        self.steps = steps

    def matches(self, sensor_history: list[tuple]):
        # we need to cut the sensor history to the length of the steps from the end
        # (we are interested in the last steps, not the first ones)
        if len(sensor_history) < len(self.steps):
            return False
        sensor_history_view = sensor_history[-len(self.steps):]
        # we are matching in the reverse order to allow for writing horizontally-ordered steps
        # (we look at them as would the robot see them from the helicopter view)
        for i in range(len(self.steps)):
            if not self.steps[-(i + 1)].matches(sensor_history_view[i][0], sensor_history_view[i][1]):
                return False
        return True


class State:
    def __init__(self, name: str, symbol: str, actions: list[Action], matcher: StateMatcher = None):
        self.name = name
        self.symbol = symbol
        self.matcher = matcher
        self.actions = actions

    def __str__(self):
        return self.name


# Actions of the robot
ACTIONS = dict(
    #  waits with wheels.stop() for button to be pressed to start moving
    START=Action("Start", 's', -1, -1),
    # moves forward, no rotation
    FWD=Action("Fwd", '|', 0b010, -1),
    #  moves forward with slight turn from the left to right (right sensor triggered, symbol for turning right)
    FWD_R=Action("Fwd-R", '/', 0b001, 0b010),
    #  moves forward with slight turn from the right to left (left sensor triggered, symbol for turning left)
    FWD_L=Action("Fwd-L", '\\', 0b100, 0b010),
    STOP=Action("Stop", '.', -1, -1),  # stops the robot
)

# States of the robot
# Each state is defined declaratively, indicating:
# - sensor history for entering the state
# - commands to execute and sensor state (series) to expect for transition from command to command
# - sensor state for leaving the state
# - supported transitions to other states
STATES = dict(
    # waits with wheels.stop() for button to be pressed to start moving
    START=State(
        name="Start", symbol='s',
        actions=[ACTIONS["START"]],
        matcher=None
    ),
    # follows the line
    LINE=State(
        name="Line", symbol='|',
        actions=[ACTIONS["FWD"], ACTIONS["FWD_L"], ACTIONS["FWD_R"]],
        matcher=None
    ),
    # detects a full intersection (+)
    INTERSECT_X=State(
        name="Intersect-+", symbol='+',
        actions=[ACTIONS["STOP"]],
        # we will be detecting normal line, then a full intersection, then normal line again
        matcher=StateMatcher([
            SensorMatcher(0b010, 10),
            SensorMatcher(0b111, 4),
            SensorMatcher(0b010, 10)
        ])
    ),
    # detects an intersection to the right
    INTERSECT_R=State(
        name="Intersect-Right", symbol='IR',
        actions=[ACTIONS["STOP"]],
        # we will be detecting normal line, then right sensor, then normal line
        matcher=StateMatcher([
            SensorMatcher(0b010, 10),
            SensorMatcher(0b011, 4),
            SensorMatcher(0b010, 10)
        ])
    ),
    # detects an intersection to the left
    INTERSECT_L=State(
        name="Intersect-Left", symbol='IL',
        actions=[ACTIONS["STOP"]],
        # we will be detecting normal line, then left sensor, then normal line
        matcher=StateMatcher([
            SensorMatcher(0b010, 10),
            SensorMatcher(0b110, 4),
            SensorMatcher(0b010, 10)
        ])
    ),
    # detects an intersection to the left and right, not forward (i.e., 'T')
    INTERSECT_T=State(
        name="Intersect-T", symbol='IT',
        actions=[ACTIONS["STOP"]],
        # we will be detecting normal line, then left and right sensor, then nothing
        matcher=StateMatcher([
            SensorMatcher(0b000, 10),
            SensorMatcher(0b110, 4),
            SensorMatcher(0b010, 10)
        ])
    ),
    # detects a turn to the right
    TURN_R=State(
        name="Turn-Right", symbol='TR',
        actions=[ACTIONS["STOP"]],
        # we will be detecting normal line, then right sensor, then nothing
        matcher=StateMatcher([
            SensorMatcher(0b000, 10),
            SensorMatcher(0b011, 4),
            SensorMatcher(0b010, 10)
        ])
    ),
    # detects a turn to the left
    TURN_L=State(
        name="Turn-Left", symbol='TL',
        actions=[ACTIONS["STOP"]],
        # we will be detecting normal line, then left sensor, then nothing
        matcher=StateMatcher([
            SensorMatcher(0b010, 10),
            SensorMatcher(0b111, 4),
            SensorMatcher(0b010, 10)
        ])
    ),
    # stops the robot
    STOP=State(
        name="Stop", symbol='.',
        actions=[ACTIONS["STOP"]],
        matcher=None
    ),
    # error state
    ERROR=State(
        name="Error",
        symbol='x',
        actions=[ACTIONS["STOP"]],
        matcher=None
    ),
)


def transition_to_state(state_now, action_now, state):
    """Transitions to state, a one-liner helper for main code."""
    state_new = STATES[state]
    action_new = state_new.actions[0]
    system.display_drive_mode(action_new.symbol)
    print("Transitioning: state %s (action %s) -> state %s (action %s)" % (state_now, action_now, state_new, action_new))
    return state_new, action_new, 0


def transition_state_action(state, action_now, lcr):
    """Transitions within the state based on the line sensor readings."""
    # print("Trans state %s action %s, %s" % (state, action_now, bin(lcr)))
    action_idx = 0
    for action in state.actions:
        if action.while_sensor == lcr:
            print("Transitioning state %s action %s to %s" % (state, action_now, action))
            system.display_drive_mode(action.symbol)
            return state, action, action_idx
        action_idx += 1
    return state, action_now, action_idx


def to_string_history(sensor_history):
    """Converts the sensor history to a string."""
    return ", ".join([str(SensorMatcher(s, c)) for s, c in sensor_history])


def match_history_to_state(sensor_history):
    """Returns the state declaring the behavior conforming to the sensor history."""
    for key, state in STATES.items():
        if state.matcher is None:
            continue
        if state.matcher.matches(sensor_history):
            print("State %s (%s) matched with history %s" % (key, state, to_string_history(sensor_history)))
            return key
    return None


if __name__ == "__main__":
    # Tries to track a line, stop at first indecision (no line for 3 secs, intersection).
    system = System()
    wheels = WheelDriver(
        system=system,
        left_pwm_min=80, left_pwm_multiplier=0.09, left_pwm_shift=-2.5,
        right_pwm_min=80, right_pwm_multiplier=0.09, right_pwm_shift=-2.5
    )
    wheels.stop()

    # Well working configurations:
    # Lenient slow (tolerance 45/2):
    # fwd_speed = 6, side_arc_min = 1, side_arc_inc = 20, side_arc_max = 20
    # Aggressive slow (tolerance 45/2):
    # fwd_speed = 6, side_arc_min = 3, side_arc_inc = 15, side_arc_max = 21
    # Recorded (tolerance 45/2):
    # fwd_speed = 9, side_speed_dec = 3, side_speed_min = 4.5, side_arc_min = 2, side_arc_inc = 4, side_arc_max = 16
    # Slight speedup (tolerance 45/2):
    # fwd_speed = 10, side_speed_dec = 4, side_speed_min = 4, side_arc_min = 3, side_arc_inc = 6, side_arc_max = 21

    # base forward speed (rad)
    fwd_speed = 10
    # how much to decrement each cycle when on side sensor (too low = lazy reaction)
    side_speed_dec = 4
    # the minimum rotation speed to maintain to not go too low
    # and unnecessarily slow down turning (it turns no matter what as long as rotation speeds are correct)
    side_speed_min = 4
    # starting arc speed (rotation) when side sensor picks up the line instead of center one
    side_arc_min = 3
    # how fast we'll be increasing arc speed each cycle we are out of center
    # this continues even if we are out of side sensor due to tolerance cycles (see below)
    side_arc_inc = 6
    # maximum arc speed we can perform (to not get too crazy and take our time when turning)
    side_arc_max = 21

    # tolerance before declaring we're out of line (time-dependent)
    # (if turning too slow, we might not catch the line again if too low)
    line_cycle_tolerance = 45
    # tolerance before assuming we are in error (hence stop, then start)
    error_cycle_tolerance = 10

    state = STATES["START"]
    action_idx = 0
    action = state.actions[action_idx]
    system.display_on()
    system.display_drive_mode(action.symbol)
    out_of_state_cycle = 0
    line_losing_cycle = 0
    # carries max speed for each wheel (for display purposes)
    # will be updated on forward to correct values
    fwd_speed_pwm_left = 255
    fwd_speed_pwm_right = 255
    # history of sensor changes: [(lcr, count), ...]
    # we keep track of the last several sensor changes and use that to determine situation underneath us
    # this feeds to a sudden main state change if we detect different behavior than expected
    # each state has the ability to override other states if it thinks it should rule the car
    sensor_history = []
    # Our history needs to be able to house at least 4 transitions
    # (going to intersection might be preceded by a single sensor if the car is going sideways)
    sensor_history_length = 5
    # But we still better disregard the transitions which last very short time (< sensor_history_fluke_transition_cycle_tolerance)
    sensor_history_eliminate_fluke_transitions_below_cycle_count = 2
    sensor_last_count = 0

    try:
        regulation_cycle_length = 20_000
        regulation_cycle_start = system.ticks_us()
        li, ri, ll, lc, lr = system.get_sensors()

        while not system.is_button_a_pressed():
            wheels.update()
            li_old, ri_old, ll_old, lc_old, lr_old = li, ri, ll, lc, lr
            li, ri, ll, lc, lr = system.get_sensors()
            if (li, ri, ll, lc, lr) != (li_old, ri_old, ll_old, lc_old, lr_old):
                if sensor_last_count > 0:
                    # we eliminate fluke transitions (short ones) from the history
                    if sensor_last_count > sensor_history_eliminate_fluke_transitions_below_cycle_count:
                        sensor_history.append(
                            (li_old << 4 | ri_old << 3 | ll_old << 2 | lc_old << 1 | lr_old, sensor_last_count))
                        if len(sensor_history) >= sensor_history_length:
                            sensor_history.pop(0)
                system.display_sensors(li, ri, ll, lc, lr)
                sensor_last_count = 1
            else:
                sensor_last_count += 1

            time_now = system.ticks_us()
            if system.ticks_diff(time_now, regulation_cycle_start) > regulation_cycle_length:
                regulation_cycle_start = time_now
                sensor_history_now = sensor_history.copy()
                sensor_history_now.append((li << 4 | ri << 3 | ll << 2 | lc << 1 | lr, sensor_last_count))
                new_state_matching_history = match_history_to_state(sensor_history_now)
                if new_state_matching_history is not None:
                    print("State change due to sensor history: %s" % new_state_matching_history)
                    state, action, action_idx = transition_to_state(state, action, new_state_matching_history)
                    sensor_history = []
                    sensor_last_count = 0

                lcr = (ll << 2) | (lc << 1) | lr
                # special actions w/o sensor dependency
                if action.while_sensor == -1 and action.until_sensor == -1:
                    if action == ACTIONS["START"]:
                        wheels.stop()
                        system.display_speed(0, fwd_speed_pwm_left, left=True)
                        system.display_speed(0, fwd_speed_pwm_right, left=False)
                        if system.is_button_b_pressed():
                            print("B pressed, starting")
                            state, action, action_idx = transition_to_state(state, action, "LINE")
                    elif action == ACTIONS["STOP"]:
                        wheels.stop()
                        if system.is_button_b_pressed():
                            state, action, action_idx = transition_to_state(state, action, "START")

                # stop immediately (no tolerance in existing state) and return to the start
                # intentionally done to not resolve more advanced situations (so we can move the robot somewhere else)
                elif lcr == 0b111:
                    out_of_state_cycle += 1
                    if out_of_state_cycle > error_cycle_tolerance:
                        state, action, action_idx = transition_to_state(state, action, "START")

                # keeping the current action within state if its while_sensor matches
                elif (((action.while_sensor == -1 or lcr == action.while_sensor) and
                       (action.until_sensor == -1 or lcr != action.until_sensor))) \
                        or out_of_state_cycle < line_cycle_tolerance:
                    if lcr == action.while_sensor:
                        if out_of_state_cycle > 0:
                            out_of_state_cycle = 0
                            print("Back in state")
                    else:
                        print(f"Transitioning: sensor={lcr:05b} no longer matches while_sensor={action.while_sensor:05b} (current state {state} action {action})")
                        state, action, action_idx = transition_state_action(state, action, lcr)
                    if action == ACTIONS["FWD"]:
                        wheels.move(speed_rad=fwd_speed, rotation_rad=0)
                        fwd_speed_pwm_left = wheels.left.speed_pwm
                        fwd_speed_pwm_right = wheels.right.speed_pwm
                        if line_losing_cycle != 1:
                            system.display_speed(fwd_speed, fwd_speed, left=True)
                            system.display_speed(fwd_speed, fwd_speed, left=False)
                        line_losing_cycle = 1  # set to 1 to immediately start with the first increment if we lose line
                    elif action == ACTIONS["FWD_L"] or action == ACTIONS["FWD_R"]:
                        line_losing_cycle += 1
                        rotation_rad = side_arc_min + side_arc_inc * line_losing_cycle
                        rotation_rad = min(rotation_rad, side_arc_max)
                        align_speed = fwd_speed - line_losing_cycle * side_speed_dec
                        align_speed = max(align_speed, side_speed_min)
                        direction = 1 if action == ACTIONS["FWD_L"] else -1
                        wheels.move(speed_rad=align_speed, rotation_rad=rotation_rad * direction)
                        system.display_speed(wheels.left.speed_pwm, fwd_speed_pwm_left, left=True)
                        system.display_speed(wheels.right.speed_pwm, fwd_speed_pwm_right, left=False)
                        print(
                            "%s, rotation_rad %d, init %s + inc_per_cycle %s * cycle %s" %
                            (action, rotation_rad, side_arc_min, side_arc_inc, line_losing_cycle))
                    elif action == ACTIONS["STOP"]:
                        wheels.stop()

                else:
                    print("Out of state exceeded %d cycles tolerance" % line_cycle_tolerance)
                    state, action, action_idx = transition_to_state(state, action, "STOP")

    finally:
        wheels.stop()
        system.display_off()
        print("Finished")
