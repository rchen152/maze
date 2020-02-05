"""Tests for maze.walls."""

import pygame
import unittest

from common import test_utils
from maze import walls


class SideTest(unittest.TestCase):

    def test_endpoints(self):
        rect = pygame.Rect(1, 2, 10, 10)
        self.assertEqual(walls.Side.TOP.endpoints(rect),
                         (rect.topleft, rect.topright))


class WallTest(test_utils.ImgTestCase):

    def setUp(self):
        super().setUp()
        self.wall = walls.ALL['wall_sright'](self.screen)

    def test_adjacent_squares(self):
        self.assertEqual(self.wall.adjacent_squares, {(0, 0), (1, 0)})

    def test_draw(self):
        self.assertFalse(self.wall.seen)
        self.wall.draw()
        self.assertTrue(self.wall.seen)


if __name__ == '__main__':
    unittest.main()