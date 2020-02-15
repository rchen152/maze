"""Objects in the play area."""

import abc
import math
import pygame
from typing import Type

from common import color
from common import img
from . import objects
from . import play_map
from . import walls

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


class _OpenGateHalf(objects.Rect):

    COLOR = color.BROWN

    def draw(self):
        super().draw()
        pygame.draw.rect(self._screen, color.BLACK, self.RECT, 1)


class OpenGateLeft(_OpenGateHalf):

    RECT = pygame.Rect(
        play_map.shift_pos(
            play_map.square_to_pos(0, 0), (316, -_OPEN_GATE_SIZE[1])),
        _OPEN_GATE_SIZE)


class OpenGateRight(_OpenGateHalf):

    RECT = pygame.Rect(
        play_map.shift_pos(
            play_map.square_to_pos(1, 0), (-320, -_OPEN_GATE_SIZE[1])),
        _OPEN_GATE_SIZE)


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
        super().__init__('fishing_rod', screen, play_map.shift_pos(
            play_map.square_to_pos(1, 2), (500, 750)), (0, -1))


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

    RECT = _HoleRect(play_map.shift_pos(
        play_map.square_to_pos(4, 2), (100, 100)), (500, 500))

    def draw(self):
        pygame.draw.circle(
            self._screen, color.BLACK, self.RECT.center, self.RECT.radius)


def _load(name, *args, **kwargs):
    return lambda screen: img.PngFactory(name, screen, *args, **kwargs)


VISIBLE = {
    **walls.ALL,
    'house': House,
    'partial_wall_gateleft': _load(
        'partial_wall_horizontal', play_map.square_to_pos(0, 0), (0, -0.5)),
    'partial_wall_gateright': _load(
        'partial_wall_horizontal', play_map.square_to_pos(1, 0),
        (-1, -0.5)),
    'gate': _load(
        'gate', play_map.shift_pos(
            play_map.square_to_pos(0, 0), (play_map.SQUARE_LENGTH / 2, 15)),
        (-0.5, -1)),
    'key': _load('key', play_map.shift_pos(
        play_map.square_to_pos(-1, 1), (150, 600))),
    'eggplant': _load('eggplant', play_map.shift_pos(
        play_map.square_to_pos(1, 1), (300, 200))),
    'fishing_rod': FishingRod,
    'lake': _load(
        'lake', play_map.shift_pos(
            play_map.square_to_pos(4, -1), (play_map.SQUARE_LENGTH / 2,) * 2),
        (-0.5, -0.5)),
    'partial_wall_catabove': _load(
        'partial_wall_vertical', play_map.square_to_pos(2, 1), (-0.5, 0)),
    'partial_wall_catbelow': _load(
        'partial_wall_vertical', play_map.square_to_pos(2, 2), (-0.5, -1)),
    'angry_cat': _load('angry_cat', play_map.shift_pos(
        play_map.square_to_pos(2, 1), (0, 400)), (-0.75, -0.5)),
    'hole': Hole,
}


HIDDEN = {
    'open_gate_left': OpenGateLeft,
    'open_gate_right': OpenGateRight,
}
