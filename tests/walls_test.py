"""Tests for maze.walls."""

import unittest

from common import test_utils
from maze import objects
from maze import walls


class WallTest(test_utils.ImgTestCase):

    def test_make(self):
        Wall = walls._Wall(0, 0, walls._WallPosition.TOP)
        self.assertIsInstance(Wall(self.screen), objects.MovablePngFactory)


if __name__ == '__main__':
    unittest.main()
