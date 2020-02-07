"""Tests for maze.walls."""

import pygame
import unittest

from common import test_utils
from maze import walls


class MatchTest(unittest.TestCase):

    def test_match(self):
        self.assertTrue(walls.match('wall_1'))

    def test_nomatch(self):
        self.assertFalse(walls.match('wallpaper'))


class SideTest(unittest.TestCase):

    def test_endpoints(self):
        rect = pygame.Rect(1, 2, 10, 10)
        self.assertEqual(walls.Side.TOP.endpoints(rect),
                         (rect.topleft, rect.topright))


class WallTest(test_utils.ImgTestCase):

    def test_adjacent_squares(self):
        wall = walls.ALL['wall_sright'](self.screen)
        self.assertEqual(wall.adjacent_squares, {(0, 0), (1, 0)})


if __name__ == '__main__':
    unittest.main()
