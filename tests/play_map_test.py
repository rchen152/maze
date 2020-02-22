"""Tests for maze.play_map."""

import unittest
from maze import play_map


class SquareToPosTest(unittest.TestCase):

    def test_start_pos(self):
        self.assertEqual(play_map.square_to_pos((0, 0)), play_map.START_POS)

    def test_shift_x(self):
        self.assertEqual(play_map.square_to_pos((-1, 0)),
                         (play_map.START_POS[0] - play_map.SQUARE_LENGTH,
                          play_map.START_POS[1]))

    def test_shift_y(self):
        self.assertEqual(play_map.square_to_pos((0, 1)),
                         (play_map.START_POS[0],
                          play_map.START_POS[1] + play_map.SQUARE_LENGTH))


class PosToSquareTest(unittest.TestCase):

    def test_start_square(self):
        self.assertEqual(play_map.pos_to_square(play_map.START_POS), (0, 0))

    def test_shift_x(self):
        pos = (play_map.START_POS[0] + play_map.SQUARE_LENGTH,
               play_map.START_POS[1])
        self.assertEqual(play_map.pos_to_square(pos), (1, 0))

    def test_shift_y(self):
        pos = (play_map.START_POS[0],
               play_map.START_POS[1] - play_map.SQUARE_LENGTH)
        self.assertEqual(play_map.pos_to_square(pos), (0, -1))


if __name__ == '__main__':
    unittest.main()
