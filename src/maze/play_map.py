"""Map positions."""

END_SQUARE = (2, 4)
SQUARE_LENGTH = 800
START_POS = (-50, -200)
HOUSE_POS = (150, -130)


def square_to_pos(*coords):
    """Returns the position of the given square."""
    return tuple(START_POS[i] + SQUARE_LENGTH * coords[i] for i in range(2))


def pos_to_square(pos):
    return tuple((pos[i] - START_POS[i]) // SQUARE_LENGTH for i in range(2))


def shift_pos(pos, shift):
    return tuple(pos[i] + shift[i] for i in range(2))
