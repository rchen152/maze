"""Tests for maze.play_area."""

import unittest

from common import test_utils
from maze import play_area


class SurfaceTest(unittest.TestCase):

    def test_init(self):
        play_area.Surface(test_utils.MockScreen())


if __name__ == '__main__':
    unittest.main()
