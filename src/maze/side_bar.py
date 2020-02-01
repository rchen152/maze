"""Side bar."""

import pygame

from common import color
from common import state
from . import objects

_SIDE_BAR_WIDTH = state.RECT.w - state.RECT.h
_SIDE_CELL_WIDTH = _SIDE_BAR_WIDTH / 3
_CREAM = (255, 250, 205)


class MiniMap(objects.Rect):

    RECT = pygame.Rect(_SIDE_CELL_WIDTH, _SIDE_CELL_WIDTH, _SIDE_CELL_WIDTH,
                       _SIDE_CELL_WIDTH)
    COLOR = color.BLACK


def ItemCell(idx):

    # Item cells are laid out in a 3x3 grid. The center square is empty because
    # the minimap goes there.
    if idx >= 4:
        idx += 1

    class ItemCell(objects.Rect):

        RECT = pygame.Rect(idx % 3 * _SIDE_CELL_WIDTH,
                           idx // 3 * _SIDE_CELL_WIDTH, _SIDE_CELL_WIDTH,
                           _SIDE_CELL_WIDTH)
        COLOR = _CREAM

        def draw(self):
            super().draw()
            pygame.draw.rect(self._screen, color.BLACK, self.RECT, 2)

    return ItemCell


class TextArea(objects.Rect):

    RECT = pygame.Rect(0, _SIDE_BAR_WIDTH, _SIDE_BAR_WIDTH,
                       state.RECT.h - _SIDE_BAR_WIDTH)
    COLOR = color.BLACK


class Surface(objects.Surface):

    RECT = pygame.Rect(state.RECT.h, 0, _SIDE_BAR_WIDTH, state.RECT.h)
    OBJECTS = (MiniMap, TextArea) + tuple(ItemCell(i) for i in range(8))
