from state import SensorHistoryStateMatcher, SensorHasCount, NoOpState
from state_generic import StartState, StopState, ErrorState
from state_line import LineState


class StateMap:
    """States of the robot.
    Each state is defined declaratively, indicating:
     - sensor history matchers for entering the state
     - supported transitions to other states
    """

    def __init__(self, stop_on_non_line_sensors=False, intersections=False):
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
        self.transitions = {
            'START': [ 'LINE', 'STOP' ],
            'LINE': [ 'STOP' ],
            'STOP': [ 'START' ],
        }

        if intersections:
            self.states.update({
                # detects a full intersection (+)
                'INTERSECT_X': NoOpState(
                    symbol='+', matchers=[
                        # we will be detecting normal line, then a full intersection, then normal line again
                        SensorHistoryStateMatcher(steps=[
                            SensorHasCount(sensor=0b010, min_count=10),
                            SensorHasCount(sensor=0b111, min_count=4),
                            SensorHasCount(sensor=0b010, min_count=10)
                        ])
                    ]
                ),
                # detects an intersection to the right
                'INTERSECT_R': NoOpState(
                    symbol='>', matchers=[
                        SensorHistoryStateMatcher(steps=[
                            SensorHasCount(sensor=0b010, min_count=10),
                            SensorHasCount(sensor=0b011, min_count=4),
                            SensorHasCount(sensor=0b010, min_count=10)
                        ])
                    ]
                ),
                # detects an intersection to the left
                'INTERSECT_L': NoOpState(
                    symbol='<', matchers=[
                        SensorHistoryStateMatcher(steps=[
                            SensorHasCount(sensor=0b010, min_count=10),
                            SensorHasCount(sensor=0b110, min_count=4),
                            SensorHasCount(sensor=0b010, min_count=10)
                        ])
                    ]
                ),
                # detects an intersection to the left and right, not forward (i.e., 'T')
                'INTERSECT_T': NoOpState(
                    symbol='T', matchers=[
                        SensorHistoryStateMatcher(steps=[
                            SensorHasCount(sensor=0b010, min_count=10),
                            SensorHasCount(sensor=0b110, min_count=4),
                            SensorHasCount(sensor=0b010, min_count=10)
                        ])
                    ]
                ),
                # detects a turn to the right
                'TURN_R': NoOpState(
                    symbol='R', matchers=[
                        SensorHistoryStateMatcher(steps=[
                            SensorHasCount(sensor=0b010, min_count=10),
                            SensorHasCount(sensor=0b011, min_count=4),
                            SensorHasCount(sensor=0b010, min_count=10)
                        ])
                    ]
                ),
                # detects a turn to the left
                'TURN_L': NoOpState(
                    symbol='L', matchers=[
                        SensorHistoryStateMatcher(steps=[
                            SensorHasCount(sensor=0b010, min_count=10),
                            SensorHasCount(sensor=0b110, min_count=4),
                            SensorHasCount(sensor=0b010, min_count=10)
                        ])
                    ]
                ),
            })
            self.transitions.update({
                'LINE': [ 'STOP', 'INTERSECT_X', 'INTERSECT_R', 'INTERSECT_L', 'INTERSECT_T', 'TURN_R', 'TURN_L' ],
                'INTERSECT_X': [ 'STOP', 'LINE' ],
                'INTERSECT_R': [ 'STOP', 'LINE' ],
                'INTERSECT_L': [ 'STOP', 'LINE' ],
                'INTERSECT_T': [ 'STOP', 'LINE' ],
                'TURN_R': [ 'STOP', 'LINE' ],
                'TURN_L': [ 'STOP', 'LINE' ],
            })

    def __str__(self):
        return "StateMap(%s)" % self.states
