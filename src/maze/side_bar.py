"""Side bar."""

import pygame
from typing import Sequence, NamedTuple, Tuple

from common import color
from common import img
from common import state
from . import objects

_SIDE_BAR_WIDTH = state.RECT.w - state.RECT.h
_SIDE_CELL_WIDTH = _SIDE_BAR_WIDTH / 3


class Rect(img.RectFactory):
    """A colored, drawable rectangle."""

    COLOR: Tuple[int, int, int]

    def draw(self):
        pygame.draw.rect(self._screen, self.COLOR, self.RECT)


class MiniMap(Rect):

    RECT = pygame.Rect(_SIDE_CELL_WIDTH, _SIDE_CELL_WIDTH, _SIDE_CELL_WIDTH,
                       _SIDE_CELL_WIDTH)
    COLOR = color.BLACK


def ItemCell(idx):

    # Item cells are laid out in a 3x3 grid. The center square is empty because
    # the minimap goes there.
    if idx >= 4:
        idx += 1

    class ItemCell(Rect):

        RECT = pygame.Rect(idx % 3 * _SIDE_CELL_WIDTH,
                           idx // 3 * _SIDE_CELL_WIDTH, _SIDE_CELL_WIDTH,
                           _SIDE_CELL_WIDTH)
        COLOR = color.LIGHT_CREAM

        def draw(self):
            super().draw()
            pygame.draw.rect(self._screen, color.BLACK, self.RECT, 2)

    return ItemCell


class _TextBlock(NamedTuple):
    pos: Tuple[int, int]
    size: Tuple[int, int]
    value: str


class TextArea(Rect):

    RECT = pygame.Rect(0, _SIDE_BAR_WIDTH, _SIDE_BAR_WIDTH,
                       state.RECT.h - _SIDE_BAR_WIDTH)
    COLOR = color.BLACK
    _LEFT_PAD = 5

    def __init__(self, screen):
        super().__init__(screen)
        self._font = pygame.font.SysFont('couriernew', 20)
        self._text: Sequence[_TextBlock] = []

    def show(self, text):
        if text is None:
            self._text = []
            return
        self._text = [_TextBlock((self._LEFT_PAD, self.RECT.y), (0, 0), '')]
        text = text.split()
        for word in text:
            current_block = self._text[-1]
            if current_block.value:
                value = current_block.value + ' ' + word
            else:
                value = word
            size = self._font.size(value)
            if size[0] <= self.RECT.w - self._LEFT_PAD:
                self._text[-1] = current_block._replace(size=size, value=value)
            else:
                y = current_block.pos[-1] + current_block.size[-1]
                self._text.append(_TextBlock(
                    (self._LEFT_PAD, y), self._font.size(word), word))

    def draw(self):
        super().draw()
        if not self._text:
            return
        for block in self._text:
            self._screen.blit(self._font.render(
                block.value, 0, color.BRIGHT_GREEN), block.pos)


class Surface(objects.Surface):

    RECT = pygame.Rect(state.RECT.h, 0, _SIDE_BAR_WIDTH, state.RECT.h)
    OBJECTS = {'mini_map': MiniMap, 'text_area': TextArea,
               **{'item_cell%d' % i: ItemCell(i) for i in range(8)}}
