"""Tests for maze.play_area."""

import unittest

from common import test_utils
from maze import play_area


class PlayerTest(test_utils.ImgTestCase):

    def test_init(self):
        play_area.Player(self.screen)


class SurfaceTest(test_utils.ImgTestCase):

    def test_init(self):
        play_area.Surface(self.screen)


if __name__ == '__main__':
    unittest.main()
