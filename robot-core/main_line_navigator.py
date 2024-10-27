from state import Behavior, Ctx
from state_map import StateMap
from system import System
from wheel_driver import WheelDriver

if __name__ == "__main__":
    # Tries to track a line, stop at first indecision (no line for 3 secs, intersection).
    system = System()
    wheels = WheelDriver(
        system=system,
        left_pwm_min=60, left_pwm_multiplier=0.09, left_pwm_shift=-2.5,
        right_pwm_min=60, right_pwm_multiplier=0.09, right_pwm_shift=-2.5
    )

    # Well working configurations:
    # Lenient slow (tolerance 45/2):
    # fwd_speed = 6, side_arc_min = 1, side_arc_inc = 20, side_arc_max = 20
    # Aggressive slow (tolerance 45/2):
    # fwd_speed = 6, side_arc_min = 3, side_arc_inc = 15, side_arc_max = 21
    # Recorded (tolerance 45/2):
    # fwd_speed = 9, side_speed_dec = 3, side_speed_min = 4.5, side_arc_min = 2, side_arc_inc = 4, side_arc_max = 16
    # Slight speedup (tolerance 45/2):
    # fwd_speed = 10, side_speed_dec = 4, side_speed_min = 4, side_arc_min = 3, side_arc_inc = 6, side_arc_max = 21

    # see Behavior class for the robot behavior definition and parameter characteristics
    behavior = Behavior(
        fwd_speed=2,
        side_speed_dec=2, side_speed_min=1,
        side_arc_min=1, side_arc_inc=3, side_arc_max=6,
        # 25ms per cycle x 75 = 1.875s outside the valid line action rules (i.e., searching for line)
        line_cycle_tolerance=75,
        turn_speed=0.2, turn_arc_speed=8,
        # 25ms per cycle x 100 = 2.5s outside the valid turn action rules (i.e., searching for 90° turned line)
        turn_cycle_tolerance=100,
        fast_sensor_change_dropped_below_cycle_count=4,
        cycle_duration_us=25_000
    )
    state_map = StateMap(behavior=behavior, stop_on_non_line_sensors=False, turns=True, intersections=True)
    ctx = Ctx(system=system, wheels=wheels, behavior=behavior,
              states=state_map.states, transitions=state_map.transitions, state_key='START')

    try:
        state_cycle_start = system.ticks_us()
        while not system.is_button_a_pressed():
            wheels.update()
            # reads the sensors and builds their history
            ctx.update_sensors()

            time_now = system.ticks_us()
            if system.ticks_diff(time_now, state_cycle_start) > ctx.behavior.cycle_duration_us:
                state_cycle_start = time_now

                # finalize context before evaluation
                # (costly operations are done here like sensor history extension with current sensor)
                ctx.before_evaluation()

                # if our context situation matches one of the states, we switch to that state
                # (this is typically based on sensor history match, but other matchers are possible)
                ctx.switch_to_state_matching_ctx_situation()

                # while being in the state we update it
                ctx.state.on_update(ctx)

    finally:
        try:
            ctx.state.on_exit(ctx)
        finally:
            wheels.stop()
            system.display_off()
            print("Finished")
