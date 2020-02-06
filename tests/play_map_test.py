"""Tests for maze.play_map."""

import unittest
from maze import play_map


class SquarePosTest(unittest.TestCase):

    def test_start_pos(self):
        self.assertEqual(play_map.square_pos(0, 0), play_map.START_POS)

    def test_shift_x(self):
        self.assertEqual(play_map.square_pos(-1, 0),
                         (play_map.START_POS[0] - play_map.SQUARE_LENGTH,
                          play_map.START_POS[1]))

    def test_shift_y(self):
        self.assertEqual(play_map.square_pos(0, 1),
                         (play_map.START_POS[0],
                          play_map.START_POS[1] + play_map.SQUARE_LENGTH))


if __name__ == '__main__':
    unittest.main()
