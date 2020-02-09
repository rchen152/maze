"""Maze walls."""

import enum
from common import img
from . import play_map


def match(name):
    return name.startswith('wall_')


def partial_match(name):
    return name.startswith('partial_wall_')


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


def _Wall(coord_x, coord_y, side):
    """Returns a wall.

    Args:
      coord_x: Horizontal distance from starting square in number of squares.
      coord_y: Vertical distance from starting square in number of squares.
      side: Which side of the square the wall is on.
    """
    wall_x, wall_y = play_map.square_to_pos(coord_x, coord_y)
    if side is Side.RIGHT:
        wall_x += play_map.SQUARE_LENGTH
    elif side is Side.BOTTOM:
        wall_y += play_map.SQUARE_LENGTH
    else:
        assert side in (Side.LEFT, Side.TOP)
    if side in (Side.LEFT, Side.RIGHT):
        img_name = 'wall_vertical'
        shift = (-0.5, 0)
    else:
        assert side in (Side.TOP, Side.BOTTOM)
        img_name = 'wall_horizontal'
        shift = (0, -0.5)

    class Wall(img.PngFactory):

        SQUARE = (coord_x, coord_y)
        SIDE = side

        def __init__(self, screen):
            super().__init__(img_name, screen, (wall_x, wall_y), shift)

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
