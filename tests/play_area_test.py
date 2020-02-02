"""Tests for maze.play_area."""

import unittest

from common import test_utils
from maze import play_area


class SurfaceTest(test_utils.ImgTestCase):

    def test_move(self):
        surface = play_area.Surface(self.screen)
        house_rect = surface.house.RECT
        surface.house.move((1, 1))
        self.assertEqual(surface.house.RECT.topleft,
                         (house_rect.x + 1, house_rect.y + 1))


if __name__ == '__main__':
    unittest.main()
