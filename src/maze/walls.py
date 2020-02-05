"""Maze walls."""

import enum
from . import objects

START_X = -50
START_Y = -200


class Side(enum.Enum):
    LEFT = enum.auto()
    RIGHT = enum.auto()
    TOP = enum.auto()
    BOTTOM = enum.auto()

    def endpoints(self, rect):
        if self is Side.LEFT:
            return (rect.topleft, rect.bottomleft)
        elif self is Side.RIGHT:
            return (rect.topright, rect.bottomright)
        elif self is Side.TOP:
            return (rect.topleft, rect.topright)
        else:
            assert self is Side.BOTTOM
            return (rect.bottomleft, rect.bottomright)


def _Wall(delta_x, delta_y, side):
    """Returns a wall.

    Args:
      delta_x: Horizontal distance from starting square in number of squares.
      delta_y: Vertical distance from starting square in number of squares.
      side: Which side of the square the wall is on.
    """
    length = 800
    wall_x = START_X + length * delta_x
    wall_y = START_Y + length * delta_y
    if side is Side.RIGHT:
        wall_x += length
    elif side is Side.BOTTOM:
        wall_y += length
    else:
        assert side in (Side.LEFT, Side.TOP)
    if side in (Side.LEFT, Side.RIGHT):
        img = 'wall_vertical'
        shift = (-0.5, 0)
    else:
        assert side in (Side.TOP, Side.BOTTOM)
        img = 'wall_horizontal'
        shift = (0, -0.5)

    class Wall(objects.MovablePngFactory):

        SQUARE = (delta_x, delta_y)
        SIDE = side

        def __init__(self, screen):
            super().__init__(img, screen, (wall_x, wall_y), shift)
            self.seen = False

        @property
        def adjacent_squares(self):
            if self.SIDE is Side.LEFT:
                square = (self.SQUARE[0] - 1, self.SQUARE[1])
            elif self.SIDE is Side.RIGHT:
                square = (self.SQUARE[0] + 1, self.SQUARE[1])
            elif self.SIDE is Side.TOP:
                square = (self.SQUARE[0], self.SQUARE[1] - 1)
            else:
                assert self.SIDE is Side.BOTTOM
                square = (self.SQUARE[0], self.SQUARE[1] + 1)
            return {self.SQUARE, square}

        def draw(self):
            super().draw()
            self.seen = True

    return Wall


ALL = {
    'wall_sright': _Wall(0, 0, Side.RIGHT),
    'wall_sbottom': _Wall(0, 0, Side.BOTTOM),
    'wall_1left': _Wall(-1, 0, Side.LEFT),
    'wall_1top': _Wall(-1, 0, Side.TOP),
    'wall_2left': _Wall(0, -1, Side.LEFT),
    'wall_2top': _Wall(0, -1, Side.TOP),
    'wall_3top': _Wall(1, -1, Side.TOP),
    'wall_3right': _Wall(1, -1, Side.RIGHT),
    'wall_6left': _Wall(0, 1, Side.LEFT),
    'wall_7bottom': _Wall(-1, 1, Side.BOTTOM),
    'wall_7left': _Wall(-1, 1, Side.LEFT),
    'wall_8top': _Wall(2, 0, Side.TOP),
    'wall_8bottom': _Wall(2, 0, Side.BOTTOM),
    'wall_9bottom': _Wall(2, 1, Side.BOTTOM),
    'wall_10left': _Wall(2, 2, Side.LEFT),
    'wall_12bottom': _Wall(0, 2, Side.BOTTOM),
    'wall_12left': _Wall(0, 2, Side.LEFT),
    'wall_13left': _Wall(3, -1, Side.LEFT),
    'wall_13top': _Wall(3, -1, Side.TOP),
    'wall_14bottom': _Wall(3, 0, Side.BOTTOM),
    'wall_15bottom': _Wall(3, 1, Side.BOTTOM),
    'wall_17right': _Wall(3, 3, Side.RIGHT),
    'wall_17bottom': _Wall(3, 3, Side.BOTTOM),
    'wall_17left': _Wall(3, 3, Side.LEFT),
    'wall_18left': _Wall(2, 3, Side.LEFT),
    'wall_19bottom': _Wall(1, 3, Side.BOTTOM),
    'wall_19left': _Wall(1, 3, Side.LEFT),
    'wall_20top': _Wall(4, -1, Side.TOP),
    'wall_20right': _Wall(4, -1, Side.RIGHT),
    'wall_21bottom': _Wall(4, 0, Side.BOTTOM),
    'wall_22right': _Wall(4, 1, Side.RIGHT),
    'wall_23right': _Wall(4, 2, Side.RIGHT),
    'wall_23bottom': _Wall(4, 2, Side.BOTTOM),
    'wall_24top': _Wall(5, 0, Side.TOP),
    'wall_24right': _Wall(5, 0, Side.RIGHT),
    'wall_25right': _Wall(5, 1, Side.RIGHT),
    'wall_25bottom': _Wall(5, 1, Side.BOTTOM),
    'wall_eright': _Wall(2, 4, Side.RIGHT),
    'wall_ebottom': _Wall(2, 4, Side.BOTTOM),
    'wall_eleft': _Wall(2, 4, Side.LEFT),
}
