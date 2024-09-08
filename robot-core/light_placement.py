class LightPlacement:
    """Defines the color scheme and placement used in the Joy-Car Robot."""
    LEFT_DIRECTION = 0
    RIGHT_DIRECTION = 1

    blinkers = {
        LEFT_DIRECTION: [1, 4],
        RIGHT_DIRECTION: [2, 7]
    }
    front_lights = [0, 3]
    back_lights = [5, 6]

    WHITE_BRIGHT = (255, 255, 255)
    WHITE_MILD = (30, 30, 30)
    ORANGE = (255, 165, 0)
    RED_BRIGHT = (255, 0, 0)
    RED_MILD = (30, 0, 0)

    initial_color_for_position = [
        WHITE_MILD, ORANGE, ORANGE, WHITE_MILD,
        ORANGE, RED_MILD, RED_MILD, ORANGE
    ]
