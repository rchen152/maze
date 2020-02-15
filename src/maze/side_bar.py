"""Side bar."""

import dataclasses
import os
import pygame
from typing import Sequence, Tuple, Union

from common import color
from common import img
from common import state
from . import objects

_SIDE_BAR_WIDTH = state.RECT.w - state.RECT.h
_SIDE_CELL_WIDTH = _SIDE_BAR_WIDTH / 3


class MiniMap(objects.Rect):

    RECT = pygame.Rect(_SIDE_CELL_WIDTH, _SIDE_CELL_WIDTH, _SIDE_CELL_WIDTH,
                       _SIDE_CELL_WIDTH)
    COLOR = color.BLACK
    _SQUARE_LENGTH = 20
    _CENTER_RECT = pygame.Rect(RECT.centerx - _SQUARE_LENGTH / 2,
                               RECT.centery - _SQUARE_LENGTH / 2,
                               _SQUARE_LENGTH, _SQUARE_LENGTH)

    def __init__(self, screen):
        super().__init__(screen)
        self._current_square = (0, 0)
        self._explored_squares = {self._current_square}
        self._seen_walls = set()
        self._current_square_color = color.BRIGHT_GREEN
        self._square_color = color.BLUE
        self._wall_color = color.LIGHT_CREAM

    def update(self, square, visible_walls):
        self._current_square = square
        self._explored_squares.add(square)
        self._seen_walls |= visible_walls

    def turn_red(self):
        self._current_square_color = self._square_color = self._wall_color = (
            color.RED)

    def draw(self):
        super().draw()
        center = tuple((max(coords) + min(coords)) / 2
                       for coords in zip(*self._explored_squares))

        def get_rect_at(index):
            return self._CENTER_RECT.move(tuple(
                (index[i] - center[i]) * self._SQUARE_LENGTH for i in range(2)))

        for square in self._explored_squares:
            if square == self._current_square:
                square_color = self._current_square_color
            else:
                square_color = self._square_color
            pygame.draw.rect(self._screen, square_color, get_rect_at(square))
        for wall in self._seen_walls:
            start_pos, end_pos = wall.SIDE.endpoints(get_rect_at(wall.SQUARE))
            pygame.draw.line(
                self._screen, self._wall_color, start_pos, end_pos, 2)


@dataclasses.dataclass
class _Item:
    name: str
    icon: img.PngFactory


def ItemCell(idx):

    # Item cells are laid out in a 3x3 grid. The center square is empty because
    # the minimap goes there.
    if idx >= 4:
        idx += 1

    class ItemCell(objects.Rect):

        RECT = pygame.Rect(idx % 3 * _SIDE_CELL_WIDTH,
                           idx // 3 * _SIDE_CELL_WIDTH, _SIDE_CELL_WIDTH,
                           _SIDE_CELL_WIDTH)
        COLOR = color.LIGHT_CREAM

        def __init__(self, screen):
            super().__init__(screen)
            self._item = None

        @property
        def item(self):
            return self._item.name if self._item else None

        def set_item(self, name):
            self._item = _Item(name, img.load(
                os.path.join('item', name), self._screen,
                (self.RECT.centerx, self.RECT.centery), (-0.5, -0.5)))

        def del_item(self):
            self._item = None

        def draw(self):
            super().draw()
            pygame.draw.rect(self._screen, color.BLACK, self.RECT, 2)
            if self._item:
                self._item.icon.draw()

    return ItemCell


@dataclasses.dataclass
class _TextBlock:
    pos: Tuple[int, int]
    size: Tuple[int, int]
    value: str


class TextArea(objects.Rect):

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
                self._text[-1].size = size
                self._text[-1].value = value
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
               **{f'item_cell{i}': ItemCell(i) for i in range(8)}}

    @property
    def _item_cells(self):
        for i in range(8):
            yield self._objects[f'item_cell{i}']

    def add_item(self, name):
        for item_cell in self._item_cells:
            if not item_cell.item:
                item_cell.set_item(name)
                return
        raise NotImplementedError(f'Cannot add item to full inventory: {name}')

    def handle_click(self, pos) -> Union[bool, str]:
        if not self.collidepoint(pos):
            return False
        pos = tuple(pos[i] - self.RECT.topleft[i] for i in range(2))
        for item_cell in self._item_cells:
            if item_cell.collidepoint(pos):
                break
        else:
            return True
        return item_cell.item or True

    def consume_item(self, name):
        for item_cell in self._item_cells:
            if item_cell.item == name:
                item_cell.del_item()
                return
        raise ValueError(f'Did not find item: {name}')
