"""Tests for maze.collisions."""

from typing import cast
import unittest
from maze import collisions


class CloserThanTest(unittest.TestCase):

    def test_closer_than(self):
        collision = collisions.Object((-3, 0), '')
        self.assertTrue(collision.closer_than((-4, 0)))

    def test_not_closer_than(self):
        collision = collisions.Object((-3, 0), '')
        self.assertFalse(collision.closer_than((-2, 0)))


class OneTest(unittest.TestCase):

    def test_object(self):
        collision = collisions.one((-3, 0), 'wall_1')
        self.assertNotIsInstance(collision, collisions.Item)
        self.assertIn('wall', collision.reason)

    def test_item(self):
        collision = cast(collisions.Item, collisions.one((-3, 0), 'key'))
        self.assertIn('key', collision.reason)
        self.assertEqual(collision.name, 'key')


if __name__ == '__main__':
    unittest.main()
