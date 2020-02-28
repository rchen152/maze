"""Objects in the play area."""

import abc
import itertools
import math
import pygame
from typing import Type

from common import color
from common import img
from . import objects
from . import play_map
from . import walls

FRUITS = ('peach', 'apple')
_OPEN_GATE_SIZE = (5, 82)


class _MultiRect(pygame.Rect, metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def _get_rects(self):
        pass

    def colliderect(self, rect):
        if not super().colliderect(rect):
            return False
        return any(
            self_rect.colliderect(rect) for self_rect in self._get_rects())


class _CustomShapePngFactory(img.PngFactory):

    _ShapeFactory: Type[_MultiRect]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.RECT = self._ShapeFactory(self.RECT.topleft, self.RECT.size)


class _HouseRect(_MultiRect):

    _ROOF_WIDTHS = (50, 110, 180, 255, 325, 395, 455, 550)
    _ROOF_STEP_HEIGHT = 25
    _BODY_INDENT = 60
    _BODY_WIDTH = 440

    def _get_rects(self):
        rects = []
        for width in self._ROOF_WIDTHS:
            y = rects[-1].bottom if rects else self.y
            rects.append(pygame.Rect(
                self.centerx - width / 2, y, width, self._ROOF_STEP_HEIGHT))
        rects.append(pygame.Rect(
            self.x + self._BODY_INDENT, rects[-1].bottom, self._BODY_WIDTH,
            self.bottom - rects[-1].bottom))
        return rects


class House(_CustomShapePngFactory):

    _ShapeFactory = _HouseRect

    def __init__(self, screen):
        super().__init__('house', screen, play_map.HOUSE_POS)


class _TreeRect(_MultiRect):

    def _get_rects(self):
        rect1 = pygame.Rect(self.x, self.y, self.w, 3 * self.h / 5)
        rect2 = pygame.Rect(
            self.x + self.w / 4 - 20, rect1.bottom, self.w / 2, 2 * self.h / 5)
        return (rect1, rect2)

    def collidepoint(self, pos):
        if not super().collidepoint(pos):
            return False
        return any(
            self_rect.collidepoint(pos) for self_rect in self._get_rects())


class TreePeach(_CustomShapePngFactory):

    _ShapeFactory = _TreeRect

    def __init__(self, screen):
        super().__init__('tree_peach', screen, play_map.shifted_square_to_pos(
            (-1, 0), (300, 150)))


class _OpenGateHalf(objects.Rect):

    COLOR = color.BROWN

    def draw(self):
        super().draw()
        pygame.draw.rect(self._screen, color.BLACK, self.RECT, 1)


class OpenGateLeft(_OpenGateHalf):

    RECT = pygame.Rect(
        play_map.shifted_square_to_pos((0, 0), (316, -_OPEN_GATE_SIZE[1])),
        _OPEN_GATE_SIZE)


class OpenGateRight(_OpenGateHalf):

    RECT = pygame.Rect(
        play_map.shifted_square_to_pos((1, 0), (-320, -_OPEN_GATE_SIZE[1])),
        _OPEN_GATE_SIZE)


def Tree(square, square_shift):
    pos = play_map.shifted_square_to_pos(square, square_shift)

    class Tree(_CustomShapePngFactory):

        _ShapeFactory = _TreeRect

        def __init__(self, screen):
            return super().__init__('tree', screen, pos)

    return Tree


class TreeApple(_CustomShapePngFactory):

    _ShapeFactory = _TreeRect

    def __init__(self, screen):
        return super().__init__(
            'tree_apple', screen,
            play_map.shifted_square_to_pos((2, 0), (200, -200)))


class _BunnyPrintsRect(_MultiRect):

    def _get_rects(self):
        return (pygame.Rect(self.left, self.bottom - 50, 40, 50),
                pygame.Rect(self.left + 20, self.bottom - 115, 50, 50),
                pygame.Rect(self.left + 70, self.top + 35, 45, 40),
                pygame.Rect(self.right - 50, self.top, 50, 35))


class BunnyPrints(_CustomShapePngFactory):

    _ShapeFactory = _BunnyPrintsRect

    def __init__(self, screen):
        super().__init__('bunny_prints', screen, play_map.shifted_square_to_pos(
            (4, 0), (600, 200)))


class _FishingRodRect(_MultiRect):

    def _get_rects(self):
        w = self.w * 0.2
        rects = [pygame.Rect(self.right - w, self.top, w, w)]
        for i in range(8):
            grow = 1.2 if i == 3 else 1
            rects.append(
                pygame.Rect(rects[-1].left - 0.5 * w, rects[-1].centery,
                            grow * w, grow * w))
        return rects

    def collidepoint(self, pos):
        if not super().collidepoint(pos):
            return False
        return any(
            self_rect.collidepoint(pos) for self_rect in self._get_rects())


class FishingRod(_CustomShapePngFactory):

    _ShapeFactory = _FishingRodRect

    def __init__(self, screen):
        super().__init__('fishing_rod', screen, play_map.shifted_square_to_pos(
            (1, 2), (500, 750)), (0, -1))


class _LakeRect(_MultiRect):

    _MEASUREMENTS = [
        (220, 535, 1),
        (165, 435, 2),
        (135, 400, 2),
        (110, 360, 2),
        (100, 190, 1),
        (90, 140, 1),
        (80, 80, 1),
        (50, 50, 2),
        (20, 20, 2),
        (0, 0, 2),
        (0, 50, 2),
        (30, 170, None),
    ]

    def _get_rects(self):
        height_unit = self.h / 20
        rects = []
        for left_indent, width_decrement, height_factor in self._MEASUREMENTS:
            x = self.x + left_indent
            y = rects[-1].bottom if rects else self.top
            w = self.w - width_decrement
            if height_factor:
                h = height_factor * height_unit
            else:
                h = self.bottom - rects[-1].bottom
            rects.append(pygame.Rect(x, y, w, h))
        return rects


class Lake(_CustomShapePngFactory):

    _ShapeFactory = _LakeRect

    def __init__(self, screen):
        pos = play_map.shifted_square_to_pos((4, -1), (410, 400))
        super().__init__('lake', screen, pos, (-0.5, -0.5))


class InvisibleWall(objects.Rect):

    RECT = pygame.Rect(
        play_map.shifted_square_to_pos((4, 1), (-10, 10)), (0, 775))
    COLOR = color.BLUE


class _HoleRect(_MultiRect):

    _WIDTHS = (180, 260, 320, 370, 410, 430, 450)
    _HEIGHT = 25

    @property
    def radius(self):
        return self.w // 2

    def _get_rects(self):
        rects = []
        for width in self._WIDTHS:
            y = self.top if not rects else rects[-1].bottom
            rects.append(
                pygame.Rect(self.centerx - width / 2, y, width, self._HEIGHT))
        rects.append(pygame.Rect(self.x, rects[-1].bottom, self.w,
                                 self.h - 2 * len(rects) * self._HEIGHT))
        for width in reversed(self._WIDTHS):
            rects.append(pygame.Rect(self.centerx - width / 2, rects[-1].bottom,
                                     width, self._HEIGHT))
        return rects

    def collidepoint(self, pos):
        if not super().collidepoint(pos):
            return False
        return math.hypot(
            *(pos[i] - self.center[i] for i in range(2))) <= self.radius


class Hole(img.RectFactory):

    RECT = _HoleRect(play_map.shifted_square_to_pos(
        (4, 2), (100, 100)), (500, 500))

    def draw(self):
        pygame.draw.circle(
            self._screen, color.BLACK, self.RECT.center, self.RECT.radius)


_PUZZLE_SLOT_SHIFT = {'L': 140, 'O': 260, 'V': 460, 'E': 580}


class _PuzzleWallRect(_MultiRect):

    def _get_rects(self):
        rects = tuple(pygame.Rect(self.x + shift, self.y, 79, 80)
                      for shift in _PUZZLE_SLOT_SHIFT.values())
        rects += (pygame.Rect(self.x, self.y + 37.5, 140, 5),
                  pygame.Rect(self.x + 220, self.y + 37.5, 40, 5),
                  pygame.Rect(self.x + 540, self.y + 37.5, 40, 5),
                  pygame.Rect(self.x + 660, self.y + 37.5, 140, 5))
        return rects


class PuzzleWall(img.RectFactory):

    RECT = _PuzzleWallRect(play_map.shifted_square_to_pos(
        (2, 4), (0, -40)), (800, 80))

    def draw(self):
        for i, rect in enumerate(self.RECT._get_rects()):
            pygame.draw.rect(self._screen, color.BROWN, rect, 5 if i < 4 else 0)


class PuzzleDoor(objects.Rect):

    RECT = pygame.Rect(play_map.shifted_square_to_pos(
        (2, 4), (340, -2.5)), (120, 5))
    COLOR = color.BROWN


class _PuzzleSlot(img.RectFactory):

    def draw(self):
        pygame.draw.rect(
            self._screen, color.BLUE, self.RECT.inflate(-10, -10), 5)


class PuzzleSlotL(_PuzzleSlot):

    RECT = pygame.Rect(play_map.shifted_square_to_pos(
        (2, 4), (_PUZZLE_SLOT_SHIFT['L'], -40)), (79, 80))


class PuzzleSlotO(_PuzzleSlot):

    RECT = pygame.Rect(play_map.shifted_square_to_pos(
        (2, 4), (_PUZZLE_SLOT_SHIFT['O'], -40)), (79, 80))


class PuzzleSlotV(_PuzzleSlot):

    RECT = pygame.Rect(play_map.shifted_square_to_pos(
        (2, 4), (_PUZZLE_SLOT_SHIFT['V'], -40)), (79, 80))


class PuzzleSlotE(_PuzzleSlot):

    RECT = pygame.Rect(play_map.shifted_square_to_pos(
        (2, 4), (_PUZZLE_SLOT_SHIFT['E'], -40)), (79, 80))


def _load(name, pos_info, shift=(0, 0)):
    assert len(pos_info) == 2
    if isinstance(pos_info[0], int):
        square = pos_info
        position = play_map.square_to_pos(square)
    else:
        square, square_shift = pos_info
        position = play_map.shifted_square_to_pos(square, square_shift)
    return lambda screen: img.PngFactory(name, screen, position, shift)


_SCENERY = {
    'house': House,
    'flowers_7': _load('flowers', ((-1, 1), (500, 200))),
    'tree_3': Tree((1, -1), (350, 25)),
    'flowers_4': _load('flowers', ((1, 0), (450, 600))),
    'flowers_5_1': _load('flowers', ((1, 1), (575, 150))),
    'flowers_5_2': _load('flowers', ((1, 1), (225, 450))),
    'tree_6': Tree((0, 1), (100, 300)),
    'tree_11': Tree((1, 2), (0, 200)),
    'flowers_12': _load('flowers', ((0, 2), (550, 500))),
    'flowers_19': _load('flowers', ((1, 3), (400, 400))),
    'tree_13': Tree((3, -1), (250, 300)),
    'flowers_14_1': _load('flowers', ((3, 0), (150, 375))),
    'flowers_14_2': _load('flowers', ((3, 0), (700, 500))),
    'flowers_21': _load('flowers', ((4, 0), (150, 300))),
    'tree_24': Tree((5, 0), (375, 400)),
    'flowers_25': _load('flowers', ((5, 1), (400, 525))),
    'flowers_15': _load('flowers', ((3, 1), (450, 325))),
    'tree_22': Tree((4, 1), (250, 100)),
    'tree_17': Tree((3, 3), (300, 225)),
    'tree_10': Tree((2, 2), (50, 275)),
    'flowers_18': _load('flowers', ((2, 3), (175, 425))),
    'flowers_e1': _load('flowers', ((2, 4), (275, 200))),
    'flowers_e2': _load('flowers', ((2, 4), (400, 200))),
    'flowers_e3': _load('flowers', ((2, 4), (252, 275))),
    'flowers_e4': _load('flowers', ((2, 4), (337, 275))),
    'flowers_e5': _load('flowers', ((2, 4), (422, 275))),
    'flowers_e6': _load('flowers', ((2, 4), (295, 350))),
    'flowers_e7': _load('flowers', ((2, 4), (380, 350))),
    'flowers_e8': _load('flowers', ((2, 4), (337, 425))),
}


_RED_HERRINGS = {
    'billboard_2': _load('billboard_down', ((0, -1), (200, 400))),
    'billboard_3': _load('billboard_left', ((1, -1), (50, 400))),
    'billboard_4': _load('billboard_down', ((1, 0), (300, 50))),
    'bunny_prints': BunnyPrints,
    'bunny': _load('bunny', ((5, 0), (200, 125))),
    'hole': Hole,
    'billboard_16': _load('billboard_right', ((3, 2), (485, 400)), (0, -0.5)),
    'billboard_10': _load('billboard_right', ((2, 2), (625, 400)), (0, -0.5)),
}


_GATE = {
    'key': _load('key', ((-1, 1), (150, 600))),
    'partial_wall_gateleft': _load(
        'partial_wall_horizontal', (0, 0), (0, -0.5)),
    'partial_wall_gateright': _load(
        'partial_wall_horizontal', (1, 0), (-1, -0.5)),
    'gate': _load(
        'gate', ((0, 0), (play_map.SQUARE_LENGTH / 2, 15)), (-0.5, -1)),
}


_ANGRY_CAT = {
    'eggplant': _load('eggplant', ((1, 1), (300, 200))),
    'trash_can': _load('trash_can', ((2, 1), (400, 100))),
    'fishing_rod': FishingRod,
    'lake': Lake,
    'partial_wall_catabove': _load('partial_wall_vertical', (2, 1), (-0.5, 0)),
    'partial_wall_catbelow': _load('partial_wall_vertical', (2, 2), (-0.5, -1)),
    'angry_cat': _load('angry_cat', ((2, 1), (0, 400)), (-0.75, -0.5)),
}


_INVISIBLE_WALL = {
    'tree_peach': TreePeach,
    'tree_apple': TreeApple,
    'partial_wall_cakeabove': _load('partial_wall_vertical', (3, 1), (-0.5, 0)),
    'cake': _load('cake', ((3, 1), (50, 400))),
    'invisible_wall': InvisibleWall,
}


_SHRUBBERY = {
    'bucket': _load('bucket', ((0, 2), (400, 400))),
    'matches': _load('matches', ((3, -1), (100, 150))),
    'doll': _load('doll', ((3, 0), (250, 475))),
    'shrubbery': _load('shrubbery', ((4, 2), (-5, -50))),
}


_BLOCK_PUZZLE = {
    'block_V': _load('block_V', ((0, -1), (50, 700))),
    'block_O': _load('block_O', ((1, 3), (25, 50))),
    'block_E': _load('block_E', ((5, 1), (625, 150))),
    'block_L': _load('block_L', ((3, 3), (600, 700))),
    'puzzle_wall': PuzzleWall,
    'puzzle_door': PuzzleDoor,
    'puzzle_slot_L': PuzzleSlotL,
    'puzzle_slot_O': PuzzleSlotO,
    'puzzle_slot_V': PuzzleSlotV,
    'puzzle_slot_E': PuzzleSlotE,
}


VISIBLE = {
    **walls.ALL,
    **_SCENERY,
    **_RED_HERRINGS,
    **_GATE,
    **_ANGRY_CAT,
    **_INVISIBLE_WALL,
    **_SHRUBBERY,
    **_BLOCK_PUZZLE,
}


HIDDEN = {
    'open_gate_left': OpenGateLeft,
    'open_gate_right': OpenGateRight,
    'happy_cat': _load('happy_cat', ((2, 1), (25, 25))),
    'fire': _load('fire', ((4, 2), (-5, -50))),
}


for block_char, slot_char in itertools.product('LOVE', repeat=2):
    HIDDEN[f'slotted_block_{block_char}_in_{slot_char}'] = _load(
        f'slotted_block_{block_char}',
        ((2, 4), (_PUZZLE_SLOT_SHIFT[slot_char], -40)))
del block_char, slot_char


STATE = ('pre_crave',)
