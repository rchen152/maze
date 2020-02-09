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


class ObtainTest(unittest.TestCase):

    def test_key(self):
        item = interactions.obtain('key')
        assert item  # for pytype
        self.assertEqual(item.name, 'key')
        self.assertTrue(item.success)
        self.assertTrue(item.consumed)
        self.assertIn('key', item.reason)

    def test_noop(self):
        self.assertIsNone(interactions.obtain('wall_1'))


class UseTest(unittest.TestCase):

    def test_name(self):
        use = interactions.use('key')
        self.assertEqual(use.name, 'gate')

    def test_reason(self):
        use = interactions.use('key')
        self.assertIn('gate', use.reason)

    def test_effects(self):
        use = interactions.use('key')
        self.assertCountEqual(
            use.effects, ('open_gate_left', 'open_gate_right'))


if __name__ == '__main__':
    unittest.main()
