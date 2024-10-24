from system import System
from wheel_driver import WheelDriver


class Action:
    def __init__(self, name, while_sensor, until_sensor):
        self.name = name
        self.while_sensor = while_sensor
        self.until_sensor = until_sensor

    def __str__(self):
        return self.name

class State:
    def __init__(self, name, symbol, entry_sensor, actions):
        self.name = name
        self.symbol = symbol
        self.entry_sensor = entry_sensor
        self.actions = actions

    def __str__(self):
        return self.name

# Actions of the robot
ACTIONS = dict(
    #  waits with wheels.stop() for button to be pressed to start moving
    START = Action("Start", -1, -1),
    # moves forward, no rotation
    FWD = Action("Fwd", 0b010, -1),
    #  moves forward with slight turn from the left to right (left sensor triggered)
    FWD_L = Action("Fwd-L", 0b100, 0b010),
    #  moves forward with slight turn from the right to left (right sensor triggered)
    FWD_R = Action("Fwd-R", 0b001, 0b010),
    #  left sharp turn (waiting for center sensor to catch the line)
    START_TURN_L = Action("Start-Turn-L", 0b110, -1),
    CONT_TURN_L = Action("Cont-Turn-L", 0b000, 0b100),
    FINISH_TURN_L = Action("Turn-L", 0b100, 0b010),
    #  right sharp turn (waiting for center sensor to catch the line)
    START_TURN_R = Action("Start-Turn-R", 0b011, -1),
    CONT_TURN_R = Action("Cont-Turn-R", 0b000, 0b001),
    FINISH_TURN_R = Action("Turn-R", 0b001, 0b010),
    STOP = Action("Stop", -1, -1), #  stops the robot
)

# States of the robot
# Each state is defined declaratively, indicating:
# - sensor state for entering the state
# - commands to execute and sensor state (series) to expect for transition from command to command
# - sensor state for leaving the state
# - supported transitions to other states
STATES = dict(
    #  waits with wheels.stop() for button to be pressed to start moving
    START = State("Start", '.', -1, [ACTIONS["START"]]),
    #  follows the line
    LINE = State("Line", '|', 0b010, [ACTIONS["FWD"], ACTIONS["FWD_L"], ACTIONS["FWD_R"]]),
    #  stops the robot
    STOP = State("stop", 's', -1,[ACTIONS["STOP"]]),
    #  error state
    ERROR = State("error", 'x', -1, [ACTIONS["STOP"]]),
)

STATE_TRANSITIONS = {
    STATES["START"]: [STATES["LINE"]],
    STATES["LINE"]: [STATES["STOP"]],
    STATES["STOP"]: [STATES["START"]],
    STATES["ERROR"]: [STATES["START"]],
}

def transition_state_to_state(state, lcr, debug=False):
    """Transitions to other state based on the current state and possible transitions."""
    print("Trans from state %s, %s" % (state, bin(lcr)))
    for next_state in STATE_TRANSITIONS[state]:
        if next_state.entry_sensor != -1 and next_state.entry_sensor == lcr:
            print("New state %s" % next_state)
            return next_state, next_state.actions[0], 0
    next_state = STATES["ERROR"]
    print("Failed finding state, using %s action %s" % (next_state, next_state.actions[0]))
    return next_state, next_state.actions[0], 0

def transition_state_action(state, action_now, lcr, keep_on_no_match):
    """Transitions within the state based on the line sensor readings."""
    print("Trans state %s action %s, %s" % (state, action_now, bin(lcr)))
    action_idx = 0
    for action in state.actions:
        if action.while_sensor == lcr:
            print("New state %s action %s" % (state, action))
            return state, action, action_idx
        action_idx += 1
    next_state, next_action, next_action_idx = transition_state_to_state(state, lcr)
    if next_state == STATES["ERROR"] and keep_on_no_match:
        print("No match, keeping action %s" % action_now)
        return state, action_now, action_idx
    else:
        return next_state, next_action, next_action_idx

if __name__ == "__main__":
    # Tries to track a line, stop at first indecision (no line for 3 secs, intersection).
    system = System()
    wheels = WheelDriver(
        system=system,
        left_pwm_min=80, left_pwm_multiplier=0.08944848, left_pwm_shift=-2.722451,
        right_pwm_min=80, right_pwm_multiplier=0.08349663, right_pwm_shift=-2.0864
    )
    wheels.stop()

    # Well working configurations:
    # Lenient:
    # tolerance = 45, fwd_speed = 6, losing_start = 1, increment_per_cycle = 20, max = start * 20
    # Aggressive:
    # tolerance = 45, fwd_speed = 6, losing_start = 3, increment_per_cycle = 15, max = start * 7

    state = STATES["START"]
    action_idx = 0
    action = state.actions[action_idx]
    out_of_state_tolerance_cycles = 45
    out_of_state_tolerance_cycles_error = 2
    out_of_state_cycle = 0
    line_losing_rotation_rad_start = 2
    line_losing_cycle = 0
    line_losing_rotation_rad_increment_per_cycle = 4
    line_losing_cycle_multiplier = 1.5
    rotation_max = line_losing_rotation_rad_start * 8
    forward_speed = 9  # radians per second
    turn_speed = 4  # radians per second
    forward_align_speed_degrader_cycle_multiplier = 3
    forward_align_speed_min = forward_speed * 0.5
    system.display_on()
    system.display_drive_mode(state.symbol)

    try:
        info_cycle_length = 500_000
        info_cycle_start = system.ticks_us()
        regulation_cycle_length = 50_000
        regulation_cycle_start = system.ticks_us()
        ll, lc, lr, li, ri = system.get_sensors()

        while not system.is_button_a_pressed():
            wheels.update()
            ll_old = ll; lc_old = lc; lr_old = lr; li_old = li; ri_old = ri
            ll, lc, lr, li, ri = system.get_sensors()
            if (ll, lc, lr, li, ri) != (ll_old, lc_old, lr_old, li_old, ri_old):
                system.display_sensors(ll, lc, lr, li, ri)

            time_now = system.ticks_us()
            if system.ticks_diff(time_now, regulation_cycle_start) > regulation_cycle_length:
                regulation_cycle_start = time_now
                lcr = (ll << 2) | (lc << 1) | lr
                # special actions w/o sensor dependency
                if action.while_sensor == -1 and action.until_sensor == -1:
                    if action == ACTIONS["START"]:
                        wheels.stop()
                        if system.is_button_b_pressed():
                            print("B pressed, starting")
                            state, action, action_idx = transition_state_action(state, action, lcr, False)
                            system.display_drive_mode(state.symbol)
                    elif action == ACTIONS["STOP"]:
                        wheels.stop()
                        if system.is_button_b_pressed():
                            state = STATES["START"]
                            action_idx = 0
                            action = state.actions[action_idx]
                            system.display_drive_mode(state.symbol)

                # stop immediately (no tolerance in existing state) and return to the start
                # intentionally done to not resolve more advanced situations (so we can move the robot somewhere else)
                elif lcr == 0b111:
                    out_of_state_cycle += 1
                    if out_of_state_cycle > out_of_state_tolerance_cycles_error:
                        state = STATES["START"]
                        action_idx = 0
                        action = state.actions[action_idx]
                        system.display_drive_mode(state.symbol)

                # keeping the current action within state if its while_sensor matches
                elif action.while_sensor == -1 or lcr == action.while_sensor:
                    out_of_state_cycle = 0
                    if action == ACTIONS["FWD"]:
                        wheels.move(speed_rad=forward_speed, rotation_rad=0)
                        line_losing_cycle = 1 # set to 1 to immediately start with the first increment if we lose line
                    elif action == ACTIONS["FWD_L"]:
                        rotation_rad = line_losing_rotation_rad_start + line_losing_rotation_rad_increment_per_cycle * line_losing_cycle * line_losing_cycle_multiplier
                        rotation_rad = min(rotation_rad, rotation_max)
                        print("FWD_L, rotation_rad %d, rad_start %s + increment_per_cycle %s * line_losing_cycle %s * mult %s" % (rotation_rad, line_losing_rotation_rad_start, line_losing_rotation_rad_increment_per_cycle, line_losing_cycle, line_losing_cycle_multiplier))
                        align_speed = forward_speed - line_losing_cycle * forward_align_speed_degrader_cycle_multiplier
                        align_speed = max(align_speed, forward_align_speed_min)
                        wheels.move(speed_rad=align_speed, rotation_rad=rotation_rad)
                        line_losing_cycle += 1
                    elif action == ACTIONS["FWD_R"]:
                        rotation_rad = line_losing_rotation_rad_start + line_losing_rotation_rad_increment_per_cycle * line_losing_cycle * line_losing_cycle_multiplier
                        rotation_rad = min(rotation_rad, rotation_max)
                        print("FWD_R, rotation_rad %d, rad_start %s - increment_per_cycle %s * line_losing_cycle %s * mult %s" % (rotation_rad, line_losing_rotation_rad_start, line_losing_rotation_rad_increment_per_cycle, line_losing_cycle, line_losing_cycle_multiplier))
                        align_speed = forward_speed - line_losing_cycle * forward_align_speed_degrader_cycle_multiplier
                        align_speed = max(align_speed, forward_align_speed_min)
                        wheels.move(speed_rad=align_speed, rotation_rad=-rotation_rad)
                        line_losing_cycle += 1
                    elif action == ACTIONS["START_TURN_L"]:
                        print("Turning left")
                        wheels.turn(speed_rad=turn_speed)
                    elif action == ACTIONS["START_TURN_R"]:
                        print("Turning right")
                        wheels.turn(speed_rad=-turn_speed)
                    elif action == ACTIONS["STOP"]:
                        wheels.stop()

                # transition to another action while waiting to reach until_sensor (i.e., during turning)
                elif (action.until_sensor != -1 and lcr == action.until_sensor):
                    state, action, action_idx = transition_state_action(state, action, lcr, keep_on_no_match=out_of_state_cycle < out_of_state_tolerance_cycles)
                    system.display_drive_mode(state.symbol)

                elif out_of_state_cycle < out_of_state_tolerance_cycles:
                    print("Out of state cycle %d of %d" % (out_of_state_cycle, out_of_state_tolerance_cycles))
                    state, action, action_idx = transition_state_action(state, action, lcr, keep_on_no_match=out_of_state_cycle < out_of_state_tolerance_cycles)
                    system.display_drive_mode(state.symbol)
                    if action == ACTIONS["FWD_L"]:
                        rotation_rad = line_losing_rotation_rad_start + line_losing_rotation_rad_increment_per_cycle * line_losing_cycle * line_losing_cycle_multiplier
                        rotation_rad = min(rotation_rad, rotation_max)
                        align_speed = forward_speed - line_losing_cycle * forward_align_speed_degrader_cycle_multiplier
                        align_speed = max(align_speed, forward_align_speed_min)
                        wheels.move(speed_rad=align_speed, rotation_rad=rotation_rad)
                        print("FWD_L, rotation_rad %d, rad_start %s + increment_per_cycle %s * line_losing_cycle %s * mult %s" % (rotation_rad, line_losing_rotation_rad_start, line_losing_rotation_rad_increment_per_cycle, line_losing_cycle, line_losing_cycle_multiplier))
                        line_losing_cycle += 1
                    elif action == ACTIONS["FWD_R"]:
                        rotation_rad = line_losing_rotation_rad_start + line_losing_rotation_rad_increment_per_cycle * line_losing_cycle * line_losing_cycle_multiplier
                        rotation_rad = min(rotation_rad, rotation_max)
                        align_speed = forward_speed - line_losing_cycle * forward_align_speed_degrader_cycle_multiplier
                        align_speed = max(align_speed, forward_align_speed_min)
                        wheels.move(speed_rad=align_speed, rotation_rad=-rotation_rad)
                        print("FWD_R, rotation_rad %d, rad_start %s - increment_per_cycle %s * line_losing_cycle %s * mult %s" % (rotation_rad, line_losing_rotation_rad_start, line_losing_rotation_rad_increment_per_cycle, line_losing_cycle, line_losing_cycle_multiplier))
                        line_losing_cycle += 1
                    out_of_state_cycle += 1

                elif out_of_state_cycle > out_of_state_tolerance_cycles:
                    print("Out of state exceeded %d cycles tolerance" % out_of_state_tolerance_cycles)
                    state, action, action_idx = transition_state_to_state(state, lcr)
                    system.display_drive_mode(state.symbol)
                    out_of_state_cycle = 0

                else:
                    print("Unknown processing condition, stopping")
                    state = STATES["STOP"]
                    action_idx = 0
                    action = state.actions[action_idx]
                    system.display_drive_mode(state.symbol)

            if system.ticks_diff(time_now, info_cycle_start) > info_cycle_length:
                info_cycle_start = time_now

                speed_msec_left = wheels.left.enc.speed_msec()
                speed_msec_right = wheels.right.enc.speed_msec()
                # print("Drive state: %s, speed: L=%.04fm/s, R=%.04fm/s, l=%s, c=%s, r=%s" % (state.name, speed_msec_left, speed_msec_right, ll, lc, lr))
    finally:
        wheels.stop()
        system.display_off()
        print("Finished")
