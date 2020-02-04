"""Maze walls."""

import enum
from . import objects


class _WallPosition(enum.Enum):
    LEFT = enum.auto()
    RIGHT = enum.auto()
    TOP = enum.auto()
    BOTTOM = enum.auto()


def _Wall(delta_x, delta_y, position):
    """Returns a wall.

    Args:
      delta_x: Horizontal distance from starting square in number of squares.
      delta_y: Vertical distance from starting square in number of squares.
      position: Which side of the square the wall is on.
    """
    starting_x = -50
    starting_y = -200
    length = 800
    wall_x = starting_x + length * delta_x
    wall_y = starting_y + length * delta_y
    if position is _WallPosition.RIGHT:
        wall_x += length
    elif position is _WallPosition.BOTTOM:
        wall_y += length
    else:
        assert position in (_WallPosition.LEFT, _WallPosition.TOP)
    if position in (_WallPosition.LEFT, _WallPosition.RIGHT):
        img = 'wall_vertical'
        shift = (-0.5, 0)
    else:
        assert position in (_WallPosition.TOP, _WallPosition.BOTTOM)
        img = 'wall_horizontal'
        shift = (0, -0.5)
    return objects.load_movable_png(img, (wall_x, wall_y), shift)


ALL = {
    'wall_sright': _Wall(0, 0, _WallPosition.RIGHT),
    'wall_sbottom': _Wall(0, 0, _WallPosition.BOTTOM),
    'wall_1left': _Wall(-1, 0, _WallPosition.LEFT),
    'wall_1top': _Wall(-1, 0, _WallPosition.TOP),
    'wall_2left': _Wall(0, -1, _WallPosition.LEFT),
    'wall_2top': _Wall(0, -1, _WallPosition.TOP),
    'wall_3top': _Wall(1, -1, _WallPosition.TOP),
    'wall_3right': _Wall(1, -1, _WallPosition.RIGHT),
    'wall_6left': _Wall(0, 1, _WallPosition.LEFT),
    'wall_7bottom': _Wall(-1, 1, _WallPosition.BOTTOM),
    'wall_7left': _Wall(-1, 1, _WallPosition.LEFT),
    'wall_8top': _Wall(2, 0, _WallPosition.TOP),
    'wall_8bottom': _Wall(2, 0, _WallPosition.BOTTOM),
    'wall_9bottom': _Wall(2, 1, _WallPosition.BOTTOM),
    'wall_10left': _Wall(2, 2, _WallPosition.LEFT),
    'wall_12bottom': _Wall(0, 2, _WallPosition.BOTTOM),
    'wall_12left': _Wall(0, 2, _WallPosition.LEFT),
    'wall_13left': _Wall(3, -1, _WallPosition.LEFT),
    'wall_13top': _Wall(3, -1, _WallPosition.TOP),
    'wall_14bottom': _Wall(3, 0, _WallPosition.BOTTOM),
    'wall_15bottom': _Wall(3, 1, _WallPosition.BOTTOM),
    'wall_17right': _Wall(3, 3, _WallPosition.RIGHT),
    'wall_17bottom': _Wall(3, 3, _WallPosition.BOTTOM),
    'wall_17left': _Wall(3, 3, _WallPosition.LEFT),
    'wall_18left': _Wall(2, 3, _WallPosition.LEFT),
    'wall_19bottom': _Wall(1, 3, _WallPosition.BOTTOM),
    'wall_19left': _Wall(1, 3, _WallPosition.LEFT),
    'wall_20top': _Wall(4, -1, _WallPosition.TOP),
    'wall_20right': _Wall(4, -1, _WallPosition.RIGHT),
    'wall_21bottom': _Wall(4, 0, _WallPosition.BOTTOM),
    'wall_22right': _Wall(4, 1, _WallPosition.RIGHT),
    'wall_23right': _Wall(4, 2, _WallPosition.RIGHT),
    'wall_23bottom': _Wall(4, 2, _WallPosition.BOTTOM),
    'wall_24top': _Wall(5, 0, _WallPosition.TOP),
    'wall_24right': _Wall(5, 0, _WallPosition.RIGHT),
    'wall_25right': _Wall(5, 1, _WallPosition.RIGHT),
    'wall_25bottom': _Wall(5, 1, _WallPosition.BOTTOM),
    'wall_eright': _Wall(2, 4, _WallPosition.RIGHT),
    'wall_ebottom': _Wall(2, 4, _WallPosition.BOTTOM),
    'wall_eleft': _Wall(2, 4, _WallPosition.LEFT),
}
