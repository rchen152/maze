"""Tests for maze.side_bar."""

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


class TextAreaTest(unittest.TestCase):

    def test_init(self):
        side_bar.TextArea(test_utils.MockScreen())


class SurfaceTest(unittest.TestCase):

    def test_init(self):
        side_bar.Surface(test_utils.MockScreen())


if __name__ == '__main__':
    unittest.main()
