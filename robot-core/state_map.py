from state import SensorHistoryStateMatcher, SensorHasCount, NoOpState
from state_generic import StartState, StopState, ErrorState
from state_line import LineState
from state_turn import LeftTurnState, RightTurnState


class StateMap:
    """States of the robot.
    Each state is defined declaratively, indicating:
     - sensor history matchers for entering the state
     - supported transitions to other states
    """

    def __init__(self, stop_on_non_line_sensors=False, turns=False, intersections=False):
        # if we want basic scenario, we will transition to stop on any non-line sensor change
        stop_matchers = None if not stop_on_non_line_sensors else [
            SensorHistoryStateMatcher(steps=[SensorHasCount(sensor=0b111, min_count=5)]),
            SensorHistoryStateMatcher(steps=[SensorHasCount(sensor=0b011, min_count=5)]),
            SensorHistoryStateMatcher(steps=[SensorHasCount(sensor=0b110, min_count=5)]),
        ]
        self.states = {
            # Generic states
            'START': StartState(symbol='s', matchers=[
                # move to start when line is detected after border states (i.e., after stop)
                SensorHistoryStateMatcher(steps=[SensorHasCount(sensor=0b010, min_count=10)]),
            ]),
            'STOP': StopState(symbol='.', matchers=stop_matchers),
            'ERROR': ErrorState(symbol='x'),

            # Follows the line (no declarative matchers enabled, we transition in and out using advanced conditions)
            'LINE': LineState(symbol='|'),
        }
        line_transitions = [ 'STOP' ]
        self.transitions = {
            'START': [ 'LINE', 'STOP' ],
            'LINE': line_transitions,
            'STOP': [ 'START' ],
        }

        if turns:
            self.states.update({
                # detects a turn to the left
                'TURN_L': LeftTurnState(
                    symbol='TL', matchers=[
                        # we are detecting disappearing line while last match shows it turning to the left
                        SensorHistoryStateMatcher(steps=[
                            SensorHasCount(sensor=0b000, min_count=20),
                            SensorHasCount(sensor=0b110, min_count=4),
                            SensorHasCount(sensor=0b010, min_count=10)
                        ])
                    ]
                ),
                # detects a turn to the right
                'TURN_R': RightTurnState(
                    symbol='TR', matchers=[
                        # we are detecting disappearing line while last match shows it turning to the right
                        SensorHistoryStateMatcher(steps=[
                            SensorHasCount(sensor=0b000, min_count=20),
                            SensorHasCount(sensor=0b011, min_count=4),
                            SensorHasCount(sensor=0b010, min_count=10)
                        ])
                    ]
                ),
            })
            line_transitions.extend(['TURN_L', 'TURN_R'])
            self.transitions.update({
                'TURN_L': [ 'STOP' ],
                'TURN_R': [ 'STOP' ],
            })

        if intersections:
            self.states.update({
                # detects a full intersection (+)
                'INTERSECT_X': NoOpState(
                    symbol='I+', matchers=[
                        # we will be detecting normal line, then a full intersection, then normal line again
                        SensorHistoryStateMatcher(steps=[
                            SensorHasCount(sensor=0b010, min_count=10),
                            SensorHasCount(sensor=0b111, min_count=4),
                            SensorHasCount(sensor=0b010, min_count=10)
                        ])
                    ]
                ),
                # detects an intersection to the left and right, not forward (i.e., 'T')
                'INTERSECT_T': NoOpState(
                    symbol='IT', matchers=[
                        SensorHistoryStateMatcher(steps=[
                            SensorHasCount(sensor=0b000, min_count=10),
                            SensorHasCount(sensor=0b111, min_count=4),
                            SensorHasCount(sensor=0b010, min_count=10)
                        ])
                    ]
                ),
                # detects an intersection slight to the left and right, not forward (i.e., 'Y')
                'INTERSECT_Y': NoOpState(
                    symbol='IY', matchers=[
                        SensorHistoryStateMatcher(steps=[
                            SensorHasCount(sensor=0b101, min_count=10),
                            SensorHasCount(sensor=0b010, min_count=4),
                        ])
                    ]
                ),
                # detects an intersection to the left
                'INTERSECT_L': NoOpState(
                    symbol='IL', matchers=[
                        # we are detecting a blip on the right sensor, it has to last for some time (speed-dependent)
                        SensorHistoryStateMatcher(steps=[
                            SensorHasCount(sensor=0b010, min_count=10),
                            SensorHasCount(sensor=0b110, min_count=4),
                            SensorHasCount(sensor=0b010, min_count=10)
                        ])
                    ]
                ),
                # detects an intersection to the right
                'INTERSECT_R': NoOpState(
                    symbol='IR', matchers=[
                        # we are detecting a blip on the right sensor, it has to last for some time (speed-dependent)
                        SensorHistoryStateMatcher(steps=[
                            SensorHasCount(sensor=0b010, min_count=10),
                            SensorHasCount(sensor=0b011, min_count=4),
                            SensorHasCount(sensor=0b010, min_count=10)
                        ])
                    ]
                )
            })
            line_transitions.extend(['INTERSECT_X', 'INTERSECT_R', 'INTERSECT_L', 'INTERSECT_T'])
            self.transitions.update({
                'INTERSECT_X': [ 'STOP'],
                'INTERSECT_R': [ 'STOP' ],
                'INTERSECT_L': [ 'STOP' ],
                'INTERSECT_T': [ 'STOP' ],
            })

        print("Working with states:")
        for state in self.states.values():
            print("* " + state.str_full())
        print("Enabled implicit state-to-state transitions:")
        for state, transitions in self.transitions.items():
            print(f"* {state} -> {transitions}")


    def __str__(self):
        return "StateMap(%s)" % self.states
