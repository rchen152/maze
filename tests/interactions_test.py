"""Tests for maze.collisions."""

import unittest
from maze import interactions


class CloserThanTest(unittest.TestCase):

    def test_closer_than(self):
        collision = interactions.Collision((-3, 0), '')
        self.assertTrue(collision.closer_than((-4, 0)))

    def test_not_closer_than(self):
        collision = interactions.Collision((-3, 0), '')
        self.assertFalse(collision.closer_than((-2, 0)))


class CollideTest(unittest.TestCase):

    def test_wall(self):
        collision = interactions.collide((-3, 0), 'wall_1')
        self.assertIn('wall', collision.reason)


if __name__ == '__main__':
    unittest.main()
