"""Tests for maze.side_bar."""

import pygame
import unittest

from common import test_utils
from maze import side_bar


class MiniMapTest(unittest.TestCase):

    def test_init(self):
        side_bar.MiniMap(test_utils.MockScreen())


class ItemCellTest(unittest.TestCase):

    def test_basic(self):
        Cell0 = side_bar.ItemCell(0)
        self.assertEqual(Cell0.RECT.topleft, (0, 0))
        Cell0(test_utils.MockScreen())

    def test_skip_center_cell(self):
        Cell4 = side_bar.ItemCell(4)
        width = Cell4.RECT.width
        self.assertEqual(Cell4.RECT.topleft, (width * 2, width))


class TextAreaTest(test_utils.GameStateTestCase):

    def setUp(self):
        super().setUp()
        self.text_area = side_bar.TextArea(self.screen)
        self.max_width = side_bar.TextArea.RECT.w - side_bar.TextArea._LEFT_PAD

    def test_one_line(self):
        self.text_area.show('This is some text.')
        block, = self.text_area._text
        self.assertEqual(block.value, 'This is some text.')

    def test_multiple_lines(self):
        pygame.font.SysFont.return_value.size = (
            lambda text: (self.max_width * len(text.split()), 10))
        self.text_area.show('Two lines.')
        block1, block2 = self.text_area._text
        self.assertEqual(block1.size, (self.max_width, 10))
        self.assertEqual(block1.value, 'Two')
        self.assertEqual(block2.size, (self.max_width, 10))
        self.assertEqual(block2.pos, (block1.pos[0], block1.pos[1] + 10))
        self.assertEqual(block2.value, 'lines.')

    def test_whitespace(self):
        pygame.font.SysFont.return_value.size = (
            lambda text: (self.max_width * len(text.split()) // 2, 10))
        self.text_area.show('Two words per line.')
        block1, block2 = self.text_area._text
        self.assertEqual(block1.value, 'Two words')
        self.assertEqual(block2.value, 'per line.')


class SurfaceTest(test_utils.GameStateTestCase):

    def test_init(self):
        side_bar.Surface(self.screen)


if __name__ == '__main__':
    unittest.main()
