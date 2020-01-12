"""Tests for maze.state."""

from common import test_utils
import unittest

from maze import state


class ShortEscapeEndingTest(test_utils.GameStateTestCase):

    def setUp(self):
        super().setUp()
        self.ending = state.ShortEscapeEnding(self.screen)

    def test_tick_to_active(self):
        self.ending.active = True
        self.ending._frame = 1
        self.ending.handle_tick(
            test_utils.MockEvent(state.ShortEscapeEnding._TICK))
        self.assertTrue(self.ending.active)

    def test_tick_to_inactive(self):
        self.ending.active = True
        self.ending._frame = 2
        self.ending.handle_tick(
            test_utils.MockEvent(state.ShortEscapeEnding._TICK))
        self.assertFalse(self.ending.active)


if __name__ == '__main__':
    unittest.main()
